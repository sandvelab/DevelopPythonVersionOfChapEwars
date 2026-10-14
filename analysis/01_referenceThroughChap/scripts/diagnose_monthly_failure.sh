#!/usr/bin/env bash
# Diagnose CH-07: the R original fails inside INLA on the monthly development data when
# chap-core drives it. Reproduces the failure on one backtest split, downloads the failed
# predict job's diagnostic artifact (the workspace R ran in), and inspects the CSVs R was
# given. Then runs one split on the same file reduced to chap's canonical input columns,
# to test whether the pre-derived columns the example file carries are the cause.
# Diagnostic only: nothing here is a reference score.
#
# Usage: diagnose_monthly_failure.sh <out_dir> <chap_venv_dir>
set -euo pipefail
PS4='+ '

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
OUT_DIR="$(mkdir -p "$1" && cd "$1" && pwd)"
VENV="$(cd "$2" && pwd)"
CHAP="$VENV/bin/chap"
PY="$VENV/bin/python"

EWARS_IMAGE=ghcr.io/chap-models/chapkit_ewars_model@sha256:959fb4f0f1b9d257a9697925f4500fd8ec4ffa9e1bb3ed7fc36e4f5c57c6ff88
PORT=8000
CONTAINER=ewars-diagnose
MONTHLY_CSV="$REPO_ROOT/Archive/dev-data/monthly_ewars/historic_data.csv"
source "$SCRIPT_DIR/backtest_settings.env"

set -x
docker rm -f "$CONTAINER" > /dev/null 2>&1 || true
docker run -d --platform linux/amd64 --name "$CONTAINER" -p "$PORT:8000" "$EWARS_IMAGE"
trap 'docker logs "$CONTAINER" > "$OUT_DIR/service_container.log" 2>&1 || true; docker rm -f "$CONTAINER" > /dev/null 2>&1 || true' EXIT
for i in $(seq 1 90); do
  if curl -fsS "http://localhost:$PORT/health" | grep -q healthy; then break; fi
  sleep 2
done
cd "$OUT_DIR"

one_split() {  # one_split <label> <csv>
  local rc=0
  "$CHAP" eval --model-name "http://localhost:$PORT" --run-config.is-chapkit-model \
    --model-configuration-yaml "$SCRIPT_DIR/ewars_config.yaml" \
    --dataset-csv "$2" --output-file "$OUT_DIR/$1.nc" \
    --backtest-params.n-periods "$N_PERIODS" --backtest-params.n-splits 1 \
    --backtest-params.stride "$STRIDE" > "$OUT_DIR/$1.chap.log" 2>&1 || rc=$?
  echo "$1 exit_code=$rc" >> "$OUT_DIR/outcomes.txt"
}

# 1. The failure, as the reference run met it.
: > "$OUT_DIR/outcomes.txt"
one_split as_archived "$MONTHLY_CSV"
artifact=$(grep -o 'diagnostic artifact [0-9A-Z]*' "$OUT_DIR/as_archived.chap.log" | head -1 | awk '{print $3}')
if [ -n "$artifact" ]; then
  curl -fsS -o "$OUT_DIR/failed_predict_workspace.zip" "http://localhost:$PORT/api/v1/artifacts/$artifact/\$download"
  rm -rf "$OUT_DIR/failed_predict_workspace"
  "$PY" -m zipfile -e "$OUT_DIR/failed_predict_workspace.zip" "$OUT_DIR/failed_predict_workspace"
  "$PY" "$SCRIPT_DIR/inspect_workspace.py" "$OUT_DIR/failed_predict_workspace" > "$OUT_DIR/workspace_inspection.txt"
fi

# 2. The same file, reduced to the columns chap-core delivers to a model.
"$PY" -c "import pandas as pd, sys; pd.read_csv(sys.argv[1], index_col=0)[['time_period','rainfall','mean_temperature','disease_cases','population','location']].to_csv(sys.argv[2], index=False)" \
  "$MONTHLY_CSV" "$OUT_DIR/monthly_canonical_columns.csv"
one_split canonical_columns "$OUT_DIR/monthly_canonical_columns.csv"
cat "$OUT_DIR/outcomes.txt"
