# Tutorial — run the original CHAP-EWARS model through chap

Generated from [[26-10-14_pythonEwarsForChap]] — batch 2.

This tutorial evaluates the R original of the CHAP-EWARS model
(`chap-models/chapkit_ewars_model`) with chap-core's backtest, from a fresh terminal.
Every `bash` block below is run verbatim, in order, as one script in an empty shell by
`analysis/01_referenceThroughChap/scripts/verify_tutorial.sh`. Its log is
`analysis/01_referenceThroughChap/results/tutorial_check/tutorial_run.log`. The commands are
the ones `scripts/run_reference_through_chap.sh` runs for the project's reference scores,
narrowed here to one dataset and one baseline.

**You need:** `git`, [`uv`](https://docs.astral.sh/uv/) and Docker, with the Docker daemon
running. Everything else is fetched by the commands below.

**Time:** the EWARS image runs R-INLA, which is built for amd64 only. On an Apple-Silicon Mac
it runs under emulation; the monthly evaluation below then takes a few minutes. The
measured times are in `results/run1/timings.tsv` beside the log.

## 1. Install chap-core, pinned

chap-core's documentation installs the CLI with `uv tool install chap-core`. That takes
the latest release and resolves its dependencies at install time, so the result changes
over time. Here chap-core is installed instead at the commit this project pins, from that
commit's own lockfile:

```bash
set -euo pipefail
mkdir -p ewars-through-chap && cd ewars-through-chap
git clone --quiet https://github.com/dhis2-chap/chap-core.git
git -C chap-core checkout --quiet b8c8f788fbc011f3d9d8a18ba9e993725023a6e4
(cd chap-core && uv sync --frozen --no-dev --python 3.13)
CHAP="$PWD/chap-core/.venv/bin/chap"
"$CHAP" --help > /dev/null
```

## 2. Get the data

The EWARS repository ships a monthly example: 23 Brazilian states, 2001-01 to 2017-06.
The file holds chap's six standard columns plus several that the R code derives itself
(`Cases`, `E`, `month`, `ID_year`, ...).

Those extra columns have to go. In a backtest, chap does not pass the observed covariates
of the forecast window to the model; it forecasts them from each location's seasonal
pattern (its `climatology` weather provider). It treats every column other than the target
as such a covariate, `month` included. So `month` reaches the R code as
`10.00000000000001`. `predict.R` uses an existing `month` column as it is, and INLA then
stops on the cyclic random walk with "Locations are too close". Reducing the file to the
six columns of the model's data contract lets the R code derive `month` itself, as it does
for any dataset chap delivers:

```bash
git clone --quiet https://github.com/chap-models/chapkit_ewars_model.git
git -C chapkit_ewars_model checkout --quiet 964eea8bfdb194ca8985723216e94f1ac63aa4f1
chap-core/.venv/bin/python -c "
import pandas as pd
cols = ['time_period', 'rainfall', 'mean_temperature', 'disease_cases', 'population', 'location']
df = pd.read_csv('chapkit_ewars_model/example_data_monthly/historic_data.csv', dtype=str, keep_default_na=False)
df[cols].to_csv('monthly.csv', index=False)
"
```

## 3. Write the model configuration

These are the defaults of the service's `EwarsConfig`, written out. The covariates have to
be listed. When a configuration file is given, chap always sends
`additional_continuous_covariates`, and a file that omits the list sends an empty one,
which means a model with no climate covariates:

```bash
cat > ewars_config.yaml <<'EOF'
user_option_values:
  n_lags: [3]
  precision: 0.01
  region_seasonal: false
additional_continuous_covariates:
  - rainfall
  - mean_temperature
EOF
```

## 4. Start the EWARS service

The image is pinned by digest. It is the image the repository's CI built from commit
`964eea8b` (tag `sha-964eea8`), and the service reports that commit as `git_revision` on
`/api/v1/info`:

```bash
docker rm -f ewars > /dev/null 2>&1 || true
docker run -d --platform linux/amd64 --name ewars -p 8000:8000 \
  ghcr.io/chap-models/chapkit_ewars_model@sha256:959fb4f0f1b9d257a9697925f4500fd8ec4ffa9e1bb3ed7fc36e4f5c57c6ff88
until curl -fsS http://localhost:8000/health | grep -q healthy; do sleep 2; done
curl -fsS http://localhost:8000/api/v1/info
echo
```

## 5. Evaluate it, and a baseline, through chap

chap's rolling-origin backtest is run with 7 splits and a 3-month horizon (the model's
default `prediction_periods`), moving forward one month per split. These are the project's
backtest settings. The `climatology` weather provider is chap's default, named here so
that the setting is visible. `builtin:seasonal_median` is one of chap-core's built-in
baselines, run through the same pipeline:

```bash
"$CHAP" eval --model-name http://localhost:8000 --run-config.is-chapkit-model \
  --model-configuration-yaml ewars_config.yaml \
  --dataset-csv monthly.csv --output-file ewars_monthly.nc \
  --backtest-params.n-periods 3 --backtest-params.n-splits 7 --backtest-params.stride 1 \
  --backtest-params.future-weather-provider climatology
"$CHAP" eval --model-name builtin:seasonal_median \
  --dataset-csv monthly.csv --output-file seasonal_median_monthly.nc \
  --backtest-params.n-periods 3 --backtest-params.n-splits 7 --backtest-params.stride 1 \
  --backtest-params.future-weather-provider climatology
```

## 6. Read the scores, and stop the service

`export-metrics` computes chap's metrics from the evaluation files: CRPS, MAE, RMSE,
interval coverage and others, one row per evaluation. Lower CRPS is better.

```bash
"$CHAP" export-metrics --input-files ewars_monthly.nc --input-files seasonal_median_monthly.nc \
  --output-file metrics.csv
cat metrics.csv
docker rm -f ewars
```

## What to expect

- The EWARS scores change a little from run to run. The R code sets no random seed, and
  chap passes none to the service, so the 1000 posterior samples per forecast differ
  between runs. The baseline's scores are identical on every run.
- Each split re-fits INLA on all data up to the split, so the evaluation takes about
  seven model fits.
- To evaluate the model on another dataset, give `--dataset-csv` a CSV with the six columns
  of step 2. Weekly data works the same way: chap passes weekly periods to the model as
  `YYYY-Wnn`, and `predict.R` reads the week number from that.

## The Python model, the same way

The Python translation is a chapkit service like the R original, in
`analysis/05_pythonModel/scripts/chapkit_ewars_python/`. Its `README.md` is the run guide: a
prediction from two CSV files, the service in Docker, and the chap evaluation above with
`--model-name` pointing at it. The guide's commands are run as written by
`analysis/05_pythonModel/04_throughChap/scripts/verify_guide.sh`, with the log in that node's
`results/guide_check/`. The differences from the steps above:

- The image is built from the folder (`docker build`) rather than pulled by digest. It has no
  amd64 pin, so it runs natively on Apple Silicon.
- The service id is `chapkit-ewars-model-python`. The configuration file and the chap
  command are the same as in steps 3 and 5.
- Repeated runs give identical scores. The sampler's seed is derived from each split's
  inputs; set `EWARS_SEED` on the container to change it.
