set -euo pipefail
REPO="$PWD"
cd "$REPO/analysis/05_pythonModel/scripts/chapkit_ewars_python"
uv sync --frozen
mkdir -p example_run
cat > example_run/config.yml <<'EOF'
n_lags: [3]
precision: 0.01
region_seasonal: false
additional_continuous_covariates: [rainfall, mean_temperature]
EOF
IN="$REPO/analysis/03_referenceHarness/results/inputs/weekly_nicaragua"
uv run python scripts/predict.py --historic "$IN/historic.csv" --future "$IN/future.csv" \
  --output example_run/predictions.csv --config example_run/config.yml
head -c 300 example_run/predictions.csv; echo
docker build -t chapkit-ewars-model-python .
docker rm -f ewars-python > /dev/null 2>&1 || true
docker run -d --name ewars-python -p 8000:8000 chapkit-ewars-model-python
until curl -fsS http://localhost:8000/health | grep -q healthy; do sleep 1; done
curl -fsS http://localhost:8000/api/v1/info | head -c 200; echo
cd "$(mktemp -d)"
git clone --quiet https://github.com/dhis2-chap/chap-core.git
git -C chap-core checkout --quiet b8c8f788fbc011f3d9d8a18ba9e993725023a6e4
(cd chap-core && uv sync --frozen --no-dev --python 3.13)
CHAP="$PWD/chap-core/.venv/bin/chap"
DATA="$REPO/analysis/01_referenceThroughChap/results/run1/inputs/weekly_nicaragua.csv"
CONFIG="$REPO/analysis/01_referenceThroughChap/scripts/ewars_config.yaml"
"$CHAP" eval --model-name http://localhost:8000 --run-config.is-chapkit-model \
  --model-configuration-yaml "$CONFIG" \
  --dataset-csv "$DATA" --output-file ewars_python_weekly.nc \
  --backtest-params.n-periods 3 --backtest-params.n-splits 7 --backtest-params.stride 1 \
  --backtest-params.future-weather-provider climatology
"$CHAP" export-metrics --input-files ewars_python_weekly.nc --output-file metrics.csv
cat metrics.csv
docker rm -f ewars-python
