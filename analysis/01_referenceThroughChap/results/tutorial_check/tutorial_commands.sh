set -euo pipefail
mkdir -p ewars-through-chap && cd ewars-through-chap
git clone --quiet https://github.com/dhis2-chap/chap-core.git
git -C chap-core checkout --quiet b8c8f788fbc011f3d9d8a18ba9e993725023a6e4
(cd chap-core && uv sync --frozen --no-dev --python 3.13)
CHAP="$PWD/chap-core/.venv/bin/chap"
"$CHAP" --help > /dev/null
git clone --quiet https://github.com/chap-models/chapkit_ewars_model.git
git -C chapkit_ewars_model checkout --quiet 964eea8bfdb194ca8985723216e94f1ac63aa4f1
chap-core/.venv/bin/python -c "
import pandas as pd
cols = ['time_period', 'rainfall', 'mean_temperature', 'disease_cases', 'population', 'location']
df = pd.read_csv('chapkit_ewars_model/example_data_monthly/historic_data.csv', dtype=str, keep_default_na=False)
df[cols].to_csv('monthly.csv', index=False)
"
cat > ewars_config.yaml <<'EOF'
user_option_values:
  n_lags: [3]
  precision: 0.01
  region_seasonal: false
additional_continuous_covariates:
  - rainfall
  - mean_temperature
EOF
docker rm -f ewars > /dev/null 2>&1 || true
docker run -d --platform linux/amd64 --name ewars -p 8000:8000 \
  ghcr.io/chap-models/chapkit_ewars_model@sha256:959fb4f0f1b9d257a9697925f4500fd8ec4ffa9e1bb3ed7fc36e4f5c57c6ff88
until curl -fsS http://localhost:8000/health | grep -q healthy; do sleep 2; done
curl -fsS http://localhost:8000/api/v1/info
echo
"$CHAP" eval --model-name http://localhost:8000 --run-config.is-chapkit-model \
  --model-configuration-yaml ewars_config.yaml \
  --dataset-csv monthly.csv --output-file ewars_monthly.nc \
  --backtest-params.n-periods 3 --backtest-params.n-splits 7 --backtest-params.stride 1 \
  --backtest-params.future-weather-provider climatology
"$CHAP" eval --model-name builtin:seasonal_median \
  --dataset-csv monthly.csv --output-file seasonal_median_monthly.nc \
  --backtest-params.n-periods 3 --backtest-params.n-splits 7 --backtest-params.stride 1 \
  --backtest-params.future-weather-provider climatology
"$CHAP" export-metrics --input-files ewars_monthly.nc --input-files seasonal_median_monthly.nc \
  --output-file metrics.csv
cat metrics.csv
docker rm -f ewars
