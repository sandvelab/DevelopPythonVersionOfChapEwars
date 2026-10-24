# chapkit-ewars-model-python

A Python translation of the CHAP-EWARS model (`chap-models/chapkit_ewars_model`, R-INLA +
`dlnm`), served with chapkit so that chap-core runs it exactly as it runs the R original. It
uses the same config fields, input columns and output (1000 samples per forecast row). It
differs in two places: `dlnmpy` builds the cross-basis, and an INLA-style Laplace
approximation written in Python does the fit. It needs no R and runs natively on Apple
Silicon.

| Path | What it is |
|---|---|
| `main.py` | The chapkit service: config schema, runner commands, service info (id `chapkit-ewars-model-python`) |
| `scripts/predict.py`, `scripts/train.py` | What chapkit runs; `predict.py` also runs on its own, on two CSV files |
| `ewars_python/` | The model: `frame.py` (data, cross-basis), `latent.py`, `laplace.py`, `inla_approx.py` (fit and sampling), `model.py` |
| `Dockerfile`, `compose.yml`, `pyproject.toml`, `uv.lock` | The image and the pinned dependencies |

**You need** [`uv`](https://docs.astral.sh/uv/), and Docker for steps 2–3. Every `bash` block
below is run, in order and from the repository root, by
`analysis/05_pythonModel/04_throughChap/scripts/verify_guide.sh`. Its log is in that node's
`results/guide_check/`.

## 1. Predict from two CSV files, without chap

The input files are those chap hands the model. `historic.csv` holds `time_period`,
`rainfall`, `mean_temperature`, `disease_cases`, `population` and `location`. `future.csv`
holds the same columns without `disease_cases`. The settings come from `config.yml` in the
working directory, in the flat form chapkit writes:

```bash
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
```

`predictions.csv` has one row per location and period with missing cases, and columns
`sample_0` … `sample_999`. Add `--diagnostics-dir <dir>` to also write the fit's posterior
summaries, in the file names R-INLA's instrumented reference uses.

## 2. Run it as a chapkit service

Build the image and start it on port 8000:

```bash
docker build -t chapkit-ewars-model-python .
docker rm -f ewars-python > /dev/null 2>&1 || true
docker run -d --name ewars-python -p 8000:8000 chapkit-ewars-model-python
until curl -fsS http://localhost:8000/health | grep -q healthy; do sleep 1; done
curl -fsS http://localhost:8000/api/v1/info | head -c 200; echo
```

To run the service without Docker, use `uv run uvicorn main:app --port 8000` in this
folder. The check script does not run this line.

## 3. Evaluate it through chap

Install chap-core at the commit this project pins, from its own lockfile. Then run chap's
backtest on the weekly development data (7 splits, 3 weeks ahead), with the same settings
the R original was evaluated with, and read the scores. This works in a fresh temporary
directory:

```bash
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
```

To evaluate your own data, give `--dataset-csv` a CSV with the six columns of step 1. Weekly
periods look like `2017-W05` and monthly ones like `2017-05`. The model settings are in the
YAML given to `--model-configuration-yaml`:

```yaml
user_option_values:
  n_lags: [3]            # lags per covariate; one value applies to all
  precision: 0.01        # prior precision of the lag coefficients
  region_seasonal: false # true adds a seasonal curve per location
additional_continuous_covariates: [rainfall, mean_temperature]   # [] for none
```

## What to expect

- **Speed.** A fit takes about 1–10 s on a laptop, depending on the data and on
  `region_seasonal`. A 7-split chap evaluation takes a few minutes, most of it chap's own
  work.
- **Reproducibility.** The same inputs give the same samples. The sampler's seed is
  derived from the input files and the config. Set `EWARS_SEED` (for example
  `docker run -e EWARS_SEED=123 …`) to choose it yourself.
- **How close it is to the R original.** See
  `analysis/06_closenessReport/results/closeness_report.md`, which reports layer by layer and
  sets the R original's own run-to-run behaviour beside it.
