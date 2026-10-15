#!/usr/bin/env bash
# The L5 noise floor: the R original evaluated through chap repeatedly, with nothing changed
# between runs. The R reference cannot be seeded through chap (CH-10), so the runs are
# unseeded and their spread is the reference's own run-to-run variability. Everything else
# is batch 2's evaluation exactly: the same chap-core commit and lockfile, the same image
# digest, the same inputs, config and backtest settings (read from node 01's files, not
# restated). Only EWARS is evaluated; the baselines are deterministic.
# Meant to run in a fresh shell (run.sh starts it under `env -i`).
#
# Usage: run_chap_repeats.sh <n_repeats> <out_dir> <work_dir>
set -euo pipefail
PS4='+ '  # CH-09
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
NODE01="$REPO_ROOT/analysis/01_referenceThroughChap"
N_REP="$1"
OUT_DIR="$(mkdir -p "$2" && cd "$2" && pwd)"
WORK_DIR="$(mkdir -p "$3" && cd "$3" && pwd)"

CHAP_CORE_URL=https://github.com/dhis2-chap/chap-core.git
CHAP_CORE_COMMIT=b8c8f788fbc011f3d9d8a18ba9e993725023a6e4
EWARS_COMMIT=964eea8bfdb194ca8985723216e94f1ac63aa4f1
EWARS_IMAGE=ghcr.io/chap-models/chapkit_ewars_model@sha256:959fb4f0f1b9d257a9697925f4500fd8ec4ffa9e1bb3ed7fc36e4f5c57c6ff88
PORT=8000
CONTAINER=ewars-reference-repeats
DATASET_NAMES=(monthly_ewars weekly_nicaragua)
source "$NODE01/scripts/backtest_settings.env"
CONFIG_YAML="$NODE01/scripts/ewars_config.yaml"
INPUTS="$NODE01/results/run1/inputs"

mkdir -p "$OUT_DIR/eval" "$OUT_DIR/metrics" "$OUT_DIR/chap_logs"
TIMINGS="$OUT_DIR/timings.tsv"
printf 'dataset\trepeat\tseconds\texit_code\n' > "$TIMINGS"

set -x
date -u
shasum -a 256 "$INPUTS"/*.csv "$CONFIG_YAML" "$NODE01/scripts/backtest_settings.env"

cd "$WORK_DIR"
git clone --quiet "$CHAP_CORE_URL" chap-core
git -C chap-core checkout --quiet "$CHAP_CORE_COMMIT"
git -C chap-core rev-parse HEAD > "$OUT_DIR/chap_core_commit.txt"
(cd chap-core && uv sync --frozen --no-dev --python 3.13)
CHAP="$WORK_DIR/chap-core/.venv/bin/chap"

docker pull --platform linux/amd64 "$EWARS_IMAGE"
docker rm -f "$CONTAINER" > /dev/null 2>&1 || true
docker run -d --platform linux/amd64 --name "$CONTAINER" -p "$PORT:8000" "$EWARS_IMAGE"
trap 'docker logs "$CONTAINER" > "$OUT_DIR/service_container.log" 2>&1 || true; docker rm -f "$CONTAINER" > /dev/null 2>&1 || true' EXIT
for i in $(seq 1 90); do
  if curl -fsS "http://localhost:$PORT/health" | grep -q healthy; then break; fi
  sleep 2
done
curl -fsS "http://localhost:$PORT/api/v1/info" > "$OUT_DIR/service_info.json"
grep -q "$EWARS_COMMIT" "$OUT_DIR/service_info.json"

for r in $(seq 1 "$N_REP"); do
  for name in "${DATASET_NAMES[@]}"; do
    start=$SECONDS rc=0
    "$CHAP" eval --model-name "http://localhost:$PORT" --run-config.is-chapkit-model \
      --model-configuration-yaml "$CONFIG_YAML" \
      --dataset-csv "$INPUTS/$name.csv" \
      --output-file "$OUT_DIR/eval/${name}__ewars_r__rep${r}.nc" \
      --backtest-params.n-periods "$N_PERIODS" \
      --backtest-params.n-splits "$N_SPLITS" \
      --backtest-params.stride "$STRIDE" \
      --backtest-params.future-weather-provider "$FUTURE_WEATHER_PROVIDER" \
      --run-config.log-file "$OUT_DIR/chap_logs/${name}__rep${r}.log" || rc=$?
    printf '%s\trep%s\t%s\t%s\n' "$name" "$r" "$((SECONDS - start))" "$rc" >> "$TIMINGS"
  done
done

for name in "${DATASET_NAMES[@]}"; do
  args=()
  for f in "$OUT_DIR"/eval/"${name}"__*.nc; do args+=(--input-files "$f"); done
  "$CHAP" export-metrics "${args[@]}" --output-file "$OUT_DIR/metrics/${name}_metrics.csv"
done
cat "$TIMINGS"
date -u
