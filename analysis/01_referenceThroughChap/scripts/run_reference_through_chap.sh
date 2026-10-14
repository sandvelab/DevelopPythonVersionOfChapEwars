#!/usr/bin/env bash
# Evaluate the R original CHAP-EWARS model, and chap-core's built-in baselines, through
# chap-core's `chap eval` on the development data. Meant to run in a fresh shell
# (run.sh starts it under `env -i`), so nothing from an interactive environment leaks in.
# Every command is traced (set -x) into the log; the tutorial's commands are taken from it.
#
# Usage: run_reference_through_chap.sh <out_dir> <work_dir>
#   out_dir   results of this run (metrics, .nc files, service info, timings)
#   work_dir  scratch: the chap-core clone and its venv, chap's run directories
set -euo pipefail
PS4='+ [$(date -u +%H:%M:%S)] '

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
OUT_DIR="$(mkdir -p "$1" && cd "$1" && pwd)"
WORK_DIR="$(mkdir -p "$2" && cd "$2" && pwd)"

# Anchors (plan §4b, batch 1; image digest pinned in batch 2).
CHAP_CORE_URL=https://github.com/dhis2-chap/chap-core.git
CHAP_CORE_COMMIT=b8c8f788fbc011f3d9d8a18ba9e993725023a6e4
EWARS_COMMIT=964eea8bfdb194ca8985723216e94f1ac63aa4f1
EWARS_IMAGE=ghcr.io/chap-models/chapkit_ewars_model@sha256:959fb4f0f1b9d257a9697925f4500fd8ec4ffa9e1bb3ed7fc36e4f5c57c6ff88
PORT=8000
CONTAINER=ewars-reference
BASELINES=(global_median seasonal_median persistence)

# Development datasets (Archive/dev-data/, batch 1). The holdout is never named here.
DATASET_NAMES=(monthly_ewars weekly_nicaragua)
DATASET_CSVS=(
  "$REPO_ROOT/Archive/dev-data/monthly_ewars/historic_data.csv"
  "$REPO_ROOT/Archive/dev-data/weekly_nicaragua/nicaragua_weekly_data_pre2018.csv"
)

source "$SCRIPT_DIR/backtest_settings.env"
CONFIG_YAML="$SCRIPT_DIR/ewars_config.yaml"
mkdir -p "$OUT_DIR/eval" "$OUT_DIR/metrics" "$OUT_DIR/chap_logs"
TIMINGS="$OUT_DIR/timings.tsv"
printf 'dataset\tmodel\tseconds\texit_code\n' > "$TIMINGS"

set -x
date -u
uname -a
uv --version
docker version --format '{{.Client.Version}} {{.Server.Version}} {{.Server.Arch}}'
git --version

# 1. chap-core at the pinned commit, installed from its own lockfile.
cd "$WORK_DIR"
git clone --quiet "$CHAP_CORE_URL" chap-core
git -C chap-core checkout --quiet "$CHAP_CORE_COMMIT"
git -C chap-core rev-parse HEAD > "$OUT_DIR/chap_core_commit.txt"
(cd chap-core && uv sync --frozen --no-dev --python 3.13)
CHAP="$WORK_DIR/chap-core/.venv/bin/chap"
"$CHAP" --help > /dev/null

# 2. The original EWARS chapkit service, from its image pinned by digest.
docker pull --platform linux/amd64 "$EWARS_IMAGE"
docker rm -f "$CONTAINER" > /dev/null 2>&1 || true
docker run -d --platform linux/amd64 --name "$CONTAINER" -p "$PORT:8000" "$EWARS_IMAGE"
trap 'docker logs "$CONTAINER" > "$OUT_DIR/service_container.log" 2>&1 || true; docker rm -f "$CONTAINER" > /dev/null 2>&1 || true' EXIT
for i in $(seq 1 90); do
  if curl -fsS "http://localhost:$PORT/health" | grep -q healthy; then break; fi
  sleep 2
done
curl -fsS "http://localhost:$PORT/health"
curl -fsS "http://localhost:$PORT/api/v1/info" > "$OUT_DIR/service_info.json"
docker inspect --format '{{index .RepoDigests 0}} {{.Architecture}}' "$EWARS_IMAGE" > "$OUT_DIR/image_digest.txt"
# The image must report the pinned EWARS commit, or it is not the reference (plan §3).
grep -q "$EWARS_COMMIT" "$OUT_DIR/service_info.json"

# 3. One chap evaluation per dataset and model, identical backtest settings for all.
run_eval() {  # run_eval <dataset_name> <csv> <model_label> <chap eval model arguments...>
  local name="$1" csv="$2" label="$3"; shift 3
  local start=$SECONDS rc=0
  "$CHAP" eval "$@" \
    --dataset-csv "$csv" \
    --output-file "$OUT_DIR/eval/${name}__${label}.nc" \
    --backtest-params.n-periods "$N_PERIODS" \
    --backtest-params.n-splits "$N_SPLITS" \
    --backtest-params.stride "$STRIDE" \
    --run-config.log-file "$OUT_DIR/chap_logs/${name}__${label}.log" || rc=$?
  printf '%s\t%s\t%s\t%s\n' "$name" "$label" "$((SECONDS - start))" "$rc" >> "$TIMINGS"
  return 0
}

cd "$WORK_DIR"
for k in "${!DATASET_NAMES[@]}"; do
  name="${DATASET_NAMES[$k]}"; csv="${DATASET_CSVS[$k]}"
  run_eval "$name" "$csv" ewars_r \
    --model-name "http://localhost:$PORT" --run-config.is-chapkit-model \
    --model-configuration-yaml "$CONFIG_YAML"
  for b in "${BASELINES[@]}"; do
    run_eval "$name" "$csv" "$b" --model-name "builtin:$b"
  done
done

# 4. chap's own metrics, one CSV per dataset over every evaluation that produced a file.
for name in "${DATASET_NAMES[@]}"; do
  args=()
  for f in "$OUT_DIR"/eval/"${name}"__*.nc; do args+=(--input-files "$f"); done
  "$CHAP" export-metrics "${args[@]}" --output-file "$OUT_DIR/metrics/${name}_metrics.csv"
done

cat "$TIMINGS"
date -u
