#!/usr/bin/env bash
# L5: the Python model, as its chapkit service image, through chap-core's backtest, exactly as
# the R original was evaluated in batch 2: the same chap-core commit and lockfile, the same
# inputs, config and backtest settings (read from node 01's files, not restated).
# The image is built from the package folder at this commit. The fit is deterministic and the
# sampler's seed is derived from each split's inputs (JC-24), so a repeat is identical; the
# runs differ by EWARS_SEED instead: run1 the derived seed, run2.. a component seed each.
# Meant to run in a fresh shell (run.sh starts it under `env -i`).
#
# Usage: run_python_through_chap.sh <n_runs> <out_dir> <work_dir>
set -euo pipefail
PS4='+ '
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
NODE="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="$(cd "$NODE/../../.." && pwd)"
NODE01="$REPO_ROOT/analysis/01_referenceThroughChap"
PKG="$NODE/../scripts/chapkit_ewars_python"
N_RUN="$1"
OUT_DIR="$(mkdir -p "$2" && cd "$2" && pwd)"
WORK_DIR="$(mkdir -p "$3" && cd "$3" && pwd)"
PORT=8002
CONTAINER=ewars-python-through-chap
DATASET_NAMES=(monthly_ewars weekly_nicaragua)
source "$NODE01/scripts/backtest_settings.env"
CONFIG_YAML="$NODE01/scripts/ewars_config.yaml"
INPUTS="$NODE01/results/run1/inputs"
mkdir -p "$OUT_DIR/eval" "$OUT_DIR/chap_logs"
TIMINGS="$OUT_DIR/timings.tsv"
printf 'dataset\trun\tewars_seed\tseconds\texit_code\n' > "$TIMINGS"

set -x
date -u
shasum -a 256 "$INPUTS"/*.csv "$CONFIG_YAML" "$NODE01/scripts/backtest_settings.env"
CHAP_PY="$(bash "$REPO_ROOT/analysis/04_fidelityMetrics/scripts/ensure_chap_core.sh" "$WORK_DIR")"
CHAP="$(dirname "$CHAP_PY")/chap"
git -C "$WORK_DIR/chap-core" rev-parse HEAD > "$OUT_DIR/chap_core_commit.txt"

TAG="chapkit-ewars-model-python:$(git -C "$REPO_ROOT" rev-parse --short HEAD)"
docker build -t "$TAG" "$PKG"
docker image inspect --format '{{.Id}}' "$TAG" > "$OUT_DIR/image_id.txt"
trap 'docker rm -f "$CONTAINER" > /dev/null 2>&1 || true' EXIT

for r in $(seq 1 "$N_RUN"); do
  if [ "$r" -eq 1 ]; then SEED_ENV=(); SEED=derived; else
    SEED="$("$CHAP_PY" -c "import hashlib; d=hashlib.sha256(b'20261014/python-through-chap/run$r').digest(); print(1+int.from_bytes(d[:4],'big')%(2**31-2))")"
    SEED_ENV=(-e "EWARS_SEED=$SEED"); fi
  docker rm -f "$CONTAINER" > /dev/null 2>&1 || true
  docker run -d --name "$CONTAINER" -p "$PORT:8000" ${SEED_ENV[@]+"${SEED_ENV[@]}"} "$TAG"
  for i in $(seq 1 60); do
    if curl -fsS "http://localhost:$PORT/health" | grep -q healthy; then break; fi
    sleep 1
  done
  curl -fsS "http://localhost:$PORT/api/v1/info" > "$OUT_DIR/service_info.json"
  for name in "${DATASET_NAMES[@]}"; do
    start=$SECONDS rc=0
    "$CHAP" eval --model-name "http://localhost:$PORT" --run-config.is-chapkit-model \
      --model-configuration-yaml "$CONFIG_YAML" \
      --dataset-csv "$INPUTS/$name.csv" --output-file "$OUT_DIR/eval/${name}__ewars_python__run$r.nc" \
      --backtest-params.n-periods "$N_PERIODS" --backtest-params.n-splits "$N_SPLITS" \
      --backtest-params.stride "$STRIDE" --backtest-params.future-weather-provider "$FUTURE_WEATHER_PROVIDER" \
      --run-config.log-file "$OUT_DIR/chap_logs/${name}__run$r.log" || rc=$?
    printf '%s\trun%s\t%s\t%s\t%s\n' "$name" "$r" "$SEED" "$((SECONDS - start))" "$rc" >> "$TIMINGS"
  done
  docker logs "$CONTAINER" > "$OUT_DIR/service_container_run$r.log" 2>&1 || true
done
date -u
