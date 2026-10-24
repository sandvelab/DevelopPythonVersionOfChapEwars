# Run the Python CHAP-EWARS model from this folder alone

This folder is self-contained. It holds a copy of the Python CHAP-EWARS model, the two
example datasets and the model configuration. Copy the folder anywhere, open a terminal in
it, and follow the steps below. Nothing here refers to the rest of the repository.

The aim of this guide is to let you run the model and see it evaluated by chap. It is not
the project's reproduction path: chap is installed at whatever version is current, not
pinned. The pinned, verified commands are in the repository's `analysis/` tree.

| What | Where |
|---|---|
| The model, as a chapkit service: code, Dockerfile, pinned dependencies | `model/` (its `README.md` describes the package) |
| Weekly example data, Nicaragua, 10 locations, as chap reads it | `data/weekly_nicaragua.csv` |
| Monthly example data, 23 locations, as chap reads it | `data/monthly_ewars.csv` |
| The same data split into a historic and a future file, for running the model without chap | `data/weekly_nicaragua/`, `data/monthly_ewars/` |
| The model configuration, in chap's form and in the model's own flat form | `config/ewars_config.yaml`, `config/predict_config.yml` |
| Where the steps below write their results | `output/` (created by the steps) |
| Where each file was copied from | `provenance.md` |

**You need**: [`uv`](https://docs.astral.sh/uv/), a Python package manager that fetches
Python itself if needed; Docker, with the daemon running; and `curl`. You do not need R.
The model's image builds and runs natively on both amd64 and Apple Silicon.

**How to use the guide**: open one terminal, go into this folder, and keep that terminal
open throughout. Copy each grey block, paste it into the terminal as a whole, press Enter,
and wait for it to finish before pasting the next one. Lines starting with `#` are comments
and are ignored by the shell. The whole guide takes about 15 minutes, most of it waiting.

## 1. Install chap, once

chap is the command-line tool of the CHAP platform. This installs its current release as a
uv tool and checks that it answers.

```bash
uv tool install chap-core
chap --version
```

If the second line says `chap` is not found, run `uv tool update-shell`, open a new
terminal in this folder, and try `chap --version` again.

## 2. Build the model's image and start it as a service

The block goes into the model's folder, builds its Docker image, starts the model as a web
service in the background, waits until it answers, prints its description, and comes back
to this folder.

```bash
cd model
# Build the image. The first build downloads its base image and takes a few minutes.
docker build -t chapkit-ewars-model-python .
# Remove a container of the same name left from an earlier run, if any. Harmless otherwise.
docker rm -f ewars-python > /dev/null 2>&1 || true
# Start the service in the background on port 8000.
docker run -d --name ewars-python -p 8000:8000 chapkit-ewars-model-python
# Wait, printing nothing, until the service answers. Normally a few seconds.
until curl -fsS http://localhost:8000/health | grep -q healthy; do sleep 1; done
# Print the service's description. It should name it chapkit-ewars-model-python.
curl -fsS http://localhost:8000/api/v1/info; echo
cd ..
```

When a line of text starting with `{"id":"chapkit-ewars-model-python"` has been printed,
the service is running on port 8000. That is where chap sends the data in the next step.
It keeps running in the background until step 4 stops it.

## 3. Evaluate the model with chap

chap runs a rolling-origin backtest: it repeatedly hides the last stretch of the data, asks
the model to forecast it, and scores the forecasts. The settings below are the ones the
project used: 7 splits, 3 periods ahead, stride 1, and climatology for the weather of the
forecast window. The weekly example takes a few minutes, most of it chap's own work.

```bash
mkdir -p output
chap eval --model-name http://localhost:8000 --run-config.is-chapkit-model \
  --model-configuration-yaml config/ewars_config.yaml \
  --dataset-csv data/weekly_nicaragua.csv --output-file output/ewars_python_weekly.nc \
  --backtest-params.n-periods 3 --backtest-params.n-splits 7 --backtest-params.stride 1 \
  --backtest-params.future-weather-provider climatology
chap export-metrics --input-files output/ewars_python_weekly.nc --output-file output/metrics_weekly.csv
cat output/metrics_weekly.csv
```

`output/metrics_weekly.csv` is one row of chap's aggregate metrics for the run. Among them is
CRPS, a probabilistic forecast error where lower is better. The project's own runs on this
data gave a CRPS of about 22 for both the Python model and the R original, so a value near
that means everything worked. The forecasts themselves are in the `.nc` file, which chap
can also plot and compare with other models; see chap's documentation.

For the monthly example, which takes about 5 minutes, paste this:

```bash
chap eval --model-name http://localhost:8000 --run-config.is-chapkit-model \
  --model-configuration-yaml config/ewars_config.yaml \
  --dataset-csv data/monthly_ewars.csv --output-file output/ewars_python_monthly.nc \
  --backtest-params.n-periods 3 --backtest-params.n-splits 7 --backtest-params.stride 1 \
  --backtest-params.future-weather-provider climatology
chap export-metrics --input-files output/ewars_python_monthly.nc --output-file output/metrics_monthly.csv
cat output/metrics_monthly.csv
```

The project's runs on the monthly data gave a CRPS of about 1120 to 1130.

## 4. Stop the service

```bash
docker rm -f ewars-python
```

## Your own data

Put a CSV with the columns `time_period`, `location`, `disease_cases`, `population`,
`rainfall` and `mean_temperature` in `data/`, and give its path to `--dataset-csv` in step
3. Weekly periods look like `2017-W05` and monthly ones like `2017-05`. The model settings
are in `config/ewars_config.yaml`:

```yaml
user_option_values:
  n_lags: [3]            # lags per covariate; one value applies to all
  precision: 0.01        # prior precision of the lag coefficients
  region_seasonal: false # true adds a seasonal curve per location
additional_continuous_covariates: [rainfall, mean_temperature]   # [] for none
```

## Running the model without chap, on two CSV files

The model can also forecast directly from a historic file (with cases) and a future file
(the same columns without cases), which is what chap hands it internally. This needs
neither chap nor Docker, and takes a few seconds once the dependencies are installed.

```bash
cd model
uv sync --frozen
uv run python scripts/predict.py \
  --historic ../data/weekly_nicaragua/historic.csv \
  --future ../data/weekly_nicaragua/future.csv \
  --config ../config/predict_config.yml \
  --output ../output/predictions_weekly.csv
cd ..
head -c 300 output/predictions_weekly.csv; echo
```

`output/predictions_weekly.csv` has one row per location and future period, with the
columns `sample_0` to `sample_999`: 1000 draws from the forecast distribution.

## Running the service without Docker

If you would rather not use Docker, open a **second** terminal in this folder and start the
service there; it keeps that terminal busy until you press Ctrl-C:

```bash
cd model
uv sync --frozen
uv run uvicorn main:app --port 8000
```

Then do step 3 in the first terminal as written. Step 4 is replaced by Ctrl-C in the
second terminal.

## If something goes wrong

- **`docker build` or `docker run` fails at once**: the Docker daemon is probably not
  running. Start Docker Desktop, or the Docker service, and retry.
- **Port 8000 is already in use**: change both `8000`s in the `docker run` line to a free
  port, and the URL in step 3 to match.
- **Step 2 never prints anything after the `until` line**: the service did not become
  healthy. Look at its log with `docker logs ewars-python`.
- **`chap eval` fails with an option it does not recognise**: a newer chap release has
  changed its command line. `chap eval --help` lists the current options; the repository
  this folder came from pins the version it used, under `analysis/`.
- **`uv tool install` or `uv sync` fails**: check that you have network access. Both
  download Python packages.

## Where this came from

Everything here is copied from the repository
[sandvelab/DevelopPythonVersionOfChapEwars](https://github.com/sandvelab/DevelopPythonVersionOfChapEwars),
which holds the full analysis: the model's source of truth, the five-layer comparison with
the R original, and every decision made in the translation. `provenance.md` lists the
source of each file and the commit it was copied at. `refresh.sh`, run from the repository
root, rebuilds the copies.
