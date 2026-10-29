# A Python version of the CHAP-EWARS model, run through chap

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23774991.svg)](https://doi.org/10.5281/zenodo.23774991)

This repository holds a **Python translation of the CHAP-EWARS disease-forecasting model**
and the complete record of how it was made and how closely it matches the original.

The model is EWARS-csd, the WHO early warning tool for climate-sensitive diseases. This
repository is a modified version of it, translated to Python. It is based on an earlier
version of [`Laith-hk/AUTO-EWARS-csd`](https://github.com/Laith-hk/AUTO-EWARS-csd), by way
of the modification step
[`chap-models/chapkit_ewars_model`](https://github.com/chap-models/chapkit_ewars_model),
which is the code translated here; both are licensed under the GPL-3.0, and so is this
repository (see [Licence](#licence)).

The R code translated, `chapkit_ewars_model`, is called the R original below. It forecasts
disease cases per location and period from past cases, population, rainfall and
temperature, using distributed-lag curves (the R package `dlnm`)
inside a Bayesian model fitted with R-INLA. It is served to the
[CHAP platform](https://github.com/dhis2-chap/chap-core) (chap-core) through a small
service wrapper, chapkit. The Python version keeps that contract exactly: the same inputs,
the same settings, the same output of 1000 forecast samples per row, and the same wrapper.
chap-core runs it the same way it runs the R original. It needs no R.

The translation and its comparison on the development data are finished. This file is the
map of what is here.

**Start here, depending on what you want:**

- *Run the Python model yourself, with the least setup*: copy the folder `python-ewars-standalone/`
  anywhere and follow its `README.md`. It holds the model, the example data and the
  configuration, and uses chap at its current release.
- *Run it the way the project did, pinned to the chap version used*: the
  [hands-on guide](#run-the-python-model-yourself-through-chap) below.
- *See how close it is to the R original*: `analysis/06_closenessReport/results/closeness_report.md`.
- *Read the code*: `analysis/05_pythonModel/scripts/chapkit_ewars_python/`, starting with its `README.md`.
- *See every decision and every obstacle in the translation*: `AI-generated/translation-record/`.
- *Understand how the work was done*: the [section on method](#how-this-repository-was-made) at the end.

## The result

**On the development data, the Python model reproduces the R original as closely as the R
original reproduces itself.**

That yardstick needs a word of explanation. The R original's fitting engine, INLA, does not
give the same answer twice on identical inputs, and now and then it produces a degenerate
fit or crashes. So the question "is the Python model close to R?" is answered by setting
every Python-versus-R distance beside the same R-versus-R distance, and no pass/fail
threshold is applied. The comparison is made at five layers, from the data going in to the
scores coming out:

| Layer | What is compared | What was found |
|---|---|---|
| 1. Data | The model frame built from the input files | Identical. |
| 2. Cross-basis | The distributed-lag design matrices, `dlnmpy` against R's `dlnm` | Equal to floating-point rounding, on every configuration variant. |
| 3. Posterior | The fitted parameters and their uncertainty | Inside the spread of INLA's own refits. One small systematic exception: a shift of a few hundredths of a standard deviation in the hyperparameters on two weekly variants. |
| 4. Forecast samples | The 1000 samples per forecast row | Python-versus-R distances cannot be told apart from R-versus-R or Python-versus-Python ones. |
| 5. chap's scores | CRPS from chap-core's rolling backtest | Python's runs overlap the R original's run-to-run range on both datasets, and both models rank the same way against chap's built-in baselines. |

The headline scores at layer 5, from the closeness report (aggregate CRPS, a probabilistic
forecast error where lower is better; one value per evaluation run):

| Dataset | R original | Python |
|---|---|---|
| Monthly example, 23 locations | 1123.9 to 1138.0 over 4 runs; 1 run crashed | 1115.7 to 1132.1 over 3 runs |
| Weekly Nicaragua, 10 locations | 21.92 to 22.10 over 5 runs | 21.95 to 22.16 over 3 runs |

*Source: the L5 table of `analysis/06_closenessReport/results/closeness_report.md`.*

Two further points about the Python model:

- **It behaves better than the original in practice.** Its fit is deterministic. None of its
  fits degenerated or crashed where INLA's did. It runs natively on Apple Silicon and takes
  1 to 11 seconds per fit.
- **Two fitting engines were built, and they agree.** The main one re-implements INLA's
  Laplace approximation in Python, following INLA's C source. The second samples the same
  posterior exactly, with NumPyro's NUTS sampler, and gives the same forecasts. That shows
  INLA's approximation is not what makes the two models agree. The second engine is slower
  and is kept in the repository, runnable.

## Where things are

| What | Where |
|---|---|
| **The Python model**, as a chapkit service with its Docker image and run guide | `analysis/05_pythonModel/scripts/chapkit_ewars_python/` |
| A self-contained copy of the model, data and configuration, with a guide that works from inside that folder alone | `python-ewars-standalone/` |
| The model code itself: data layer, cross-basis, latent structure, Laplace fit, sampling | `analysis/05_pythonModel/scripts/chapkit_ewars_python/ewars_python/` |
| **The closeness report**: Python versus R at five layers, beside R versus R | `analysis/06_closenessReport/results/closeness_report.md` |
| **The judgment-call list**: every decision made in the translation, its alternatives, and who made it | `AI-generated/translation-record/judgment-calls.md` |
| **The challenges overview**: every obstacle met, and how it was handled | `AI-generated/translation-record/challenges.md` |
| Tutorial: running the R original through chap, from a fresh terminal | `AI-generated/26-10-14_tutorialRunOriginalEwarsThroughChap.md` |
| The second fitting engine (NUTS) and its comparison with the first and with R | `analysis/05_pythonModel/03_inference/b_mcmcNuts/` |
| INLA's engine as read from its C source, with line citations | `analysis/05_pythonModel/03_inference/a_laplaceCcd/results/inla_spec.md` |
| The translation inventory: every R call the original makes and its Python counterpart | `analysis/02_translationInventory/results/` |
| What the R original does when nothing but the seed changes | `analysis/03_referenceHarness/`, `analysis/04_fidelityMetrics/` |
| Batch reports: what happened in each step of the work, in order | `AI-generated/batch-reports/` |
| The plan that was executed, with the decisions settled along the way | `Human-input/Plans for AI generation/26-10-14_pythonEwarsForChap.md` |
| The pinned sources: chap-core, chapkit, the R model, dlnmpy, the R-INLA and dlnm sources, the data | `Archive/` (each folder has a `provenance.md`) |
| The pinned Python environment of the analysis | `environment/` |

The analysis is organised as a tree of questions under `analysis/`. Each folder is one
question: its `claim.md` states the question and, once run, the answer it yielded; its
`run.sh` runs it; its `scripts/`, `results/` and `provenance/` hold the rest. The top-level
question and its answer are in `analysis/claim.md`.

## What was not done, and is left as future work

The purpose of the project was to show that a faithful Python translation can be made, and
to establish how close it is on the development data. That is done. The plan also foresaw
three further phases. They are **optional future work** and have not been run:

- **Stability**: a costed set of perturbations over the judgment calls, reporting the
  distribution of the Python-versus-R gap rather than a single number.
- **Held-out validation**: one opening of the sealed holdout data in `Archive/holdout/`,
  against a manifest frozen beforehand. **The holdout is still sealed.** No number from it
  has been seen.
- **Claims and manuscript**: a claim collection drawn from the tree, and an article. Both
  folders under `Human-AI-collaboration/` are empty.

So the result above is a development-data result, for the two datasets named in
`readme-at-start.md`. The plan's batch ledger (its §6) records these phases as deferred.

## Run the Python model yourself, through chap

A hands-on guide for a person at a terminal, pinned to the chap-core version the project
used. If you only want to see the model run, `python-ewars-standalone/` is the shorter
route: it is self-contained and installs chap as a uv tool. Every command here is copied
from the model's own run guide, `analysis/05_pythonModel/scripts/chapkit_ewars_python/README.md`, whose blocks
are run verbatim and checked by `analysis/05_pythonModel/04_throughChap/scripts/verify_guide.sh`.
Its log is in that node's `results/guide_check/`.

**How to use it**: open one terminal and keep it open for the whole guide. Copy each grey
block below, paste it into the terminal as a whole, press Enter, and wait for it to finish
before pasting the next one. The blocks build on each other, so paste them in order. The
lines starting with `#` are comments, which the shell ignores.

**You need**: `git`, `curl`, Docker with the daemon running, and
[`uv`](https://docs.astral.sh/uv/), a Python package manager that fetches Python 3.13 itself
if it is missing. You do not need R. The image builds and runs natively on both amd64 and
Apple Silicon. The whole guide takes roughly 15 minutes, most of it waiting.

### 1. Get the repository

```bash
git clone https://github.com/sandvelab/DevelopPythonVersionOfChapEwars.git
cd DevelopPythonVersionOfChapEwars
REPO="$PWD"
```

Everything the steps below read is tracked in git: the model, the example data, and the
configuration file the R original was evaluated with. The `REPO` variable is used by the
later steps, so keep the same terminal open.

### 2. Build the model's image and start it as a service

Paste the whole block. It goes to the model's folder, builds the Docker image, starts it in
the background, waits until it answers, and prints its description.

```bash
cd "$REPO/analysis/05_pythonModel/scripts/chapkit_ewars_python"
# Build the image. The first build downloads its base image and takes a few minutes.
docker build -t chapkit-ewars-model-python .
# Remove a container of the same name from an earlier run, if there is one. Harmless otherwise.
docker rm -f ewars-python > /dev/null 2>&1 || true
# Start the service in the background on port 8000.
docker run -d --name ewars-python -p 8000:8000 chapkit-ewars-model-python
# Wait, printing nothing, until the service answers. This normally takes a few seconds.
until curl -fsS http://localhost:8000/health | grep -q healthy; do sleep 1; done
# Print the service's description. It should name it chapkit-ewars-model-python.
curl -fsS http://localhost:8000/api/v1/info; echo
```

When the last line has printed a line of text starting with `{"id":"chapkit-ewars-model-python"`,
the service is running and listening on port 8000. That is where chap will send the data
in step 4. It keeps running in the background until step 5 stops it.

### 3. Install chap-core at the version this project used

chap-core is installed from its own lockfile at the pinned commit, so the result does not
drift with later releases. This happens in a fresh temporary directory and leaves the
repository untouched. It takes a minute or two.

```bash
cd "$(mktemp -d)"
git clone --quiet https://github.com/dhis2-chap/chap-core.git
git -C chap-core checkout --quiet b8c8f788fbc011f3d9d8a18ba9e993725023a6e4
(cd chap-core && uv sync --frozen --no-dev --python 3.13)
CHAP="$PWD/chap-core/.venv/bin/chap"
```

### 4. Run chap's backtest evaluation and read the scores

This runs the same rolling-origin backtest the project used for both models: 7 splits, 3
periods ahead, stride 1, climatology for future weather. The example is the weekly Nicaragua
development data. It takes a few minutes, most of it chap's own work.

```bash
DATA="$REPO/analysis/01_referenceThroughChap/results/run1/inputs/weekly_nicaragua.csv"
CONFIG="$REPO/analysis/01_referenceThroughChap/scripts/ewars_config.yaml"
"$CHAP" eval --model-name http://localhost:8000 --run-config.is-chapkit-model \
  --model-configuration-yaml "$CONFIG" \
  --dataset-csv "$DATA" --output-file ewars_python_weekly.nc \
  --backtest-params.n-periods 3 --backtest-params.n-splits 7 --backtest-params.stride 1 \
  --backtest-params.future-weather-provider climatology
"$CHAP" export-metrics --input-files ewars_python_weekly.nc --output-file metrics.csv
cat metrics.csv
```

`metrics.csv` is one row of chap's aggregate metrics for the run, with CRPS among them. The
weekly CRPS should land near the Python values in the table above. The project's own runs
of this command are in `analysis/05_pythonModel/04_throughChap/results/`, and the R
original's in `analysis/01_referenceThroughChap/results/`, if you want to compare. For the
monthly example, point `DATA` at `monthly_ewars.csv` in the same folder; that run takes
about 5 minutes.

### 5. Stop the service

```bash
docker rm -f ewars-python
```

### If something goes wrong

- **`docker build` or `docker run` fails at once**: the Docker daemon is probably not
  running. Start Docker Desktop, or the Docker service, and retry.
- **Port 8000 is already in use**: change both `8000`s in the `docker run` line to a free
  port, and the URL in step 4 to match.
- **Step 2 never prints anything after the `until` line**: the service did not become
  healthy. Look at its log with `docker logs ewars-python`.
- **Step 3 fails at `uv sync`**: check that `uv` is installed and that you have network
  access. It needs to download Python 3.13 and chap-core's dependencies.

### Your own data

Give `--dataset-csv` a CSV with the columns `time_period`, `location`, `disease_cases`,
`population`, `rainfall` and `mean_temperature`. Weekly periods look like `2017-W05` and
monthly ones like `2017-05`. The model settings are the YAML passed to
`--model-configuration-yaml`:

```yaml
user_option_values:
  n_lags: [3]            # lags per covariate; one value applies to all
  precision: 0.01        # prior precision of the lag coefficients
  region_seasonal: false # true adds a seasonal curve per location
additional_continuous_covariates: [rainfall, mean_temperature]   # [] for none
```

### Without chap, and without Docker

The model also predicts directly from two CSV files, a historic one with cases and a future
one without, through `scripts/predict.py` in the service folder. Step 1 of the model's run
guide shows the exact command on the example data. To run the service without Docker, run
`uv sync --frozen` and then `uv run uvicorn main:app --port 8000` in the service folder.

### Running the R original for comparison

The tutorial `AI-generated/26-10-14_tutorialRunOriginalEwarsThroughChap.md` does the same
evaluation with the R original's pinned image. That image is built for amd64 only, so on
Apple Silicon it runs under emulation and is slower.

## Reproducing the analysis

`analysis/run.sh` reproduces the whole reported analysis, following the main path at every
fork. It needs the pinned environment, built from `environment/lock.txt` by
`environment/install-env.sh`, and Docker for the nodes that run the R original or chap. The
R original's nodes need its amd64 image, and the R harness and the repeated chap
evaluations take hours. The second fitting engine is not on the main path; its own
`run.sh` under `analysis/05_pythonModel/03_inference/b_mcmcNuts/` runs it, in about 2 hours.
Every result file has a provenance record beside it, binding it to the script, inputs,
environment, seeds and commit that produced it.

## How this repository was made

The project was carried out by an agentic AI system (Claude Code) working under the
standing instructions in `AGENTS.md`, from a plan written by the human researcher, one
batch at a time, with the human settling the decisions each batch raised. The repository
started as a copy of the
[agentic-model-development-start](https://github.com/sandvelab/agentic-model-development-start)
template and follows its method: every reported number comes from a file that was executed,
no output is edited in place, every judgment call is recorded with its alternatives, and the
paths not taken stay in the tree, runnable. Every decision carries who made it, and whether
the information behind it was retrieved by the agent or pointed to by the human.

The method documents are kept because they are part of the record, and two runs under
different instructions are two different methods. None of them is needed to use the
results above.

| File | What it is |
|---|---|
| `readme-at-start.md` | The one-page statement of this project: what was pinned, what was fixed, where it stands. |
| `AGENTS.md` | The instructions the agent worked under. `CLAUDE.md` only points to it. |
| `MOTIVATION.md` | Why the repository is shaped the way it is. |
| `setup-guide.md`, `How-to-use-vault.md`, `folder-structure.md` | The template's own guides: how a project is started from a fresh copy, and what each folder is for. |
| `AI-internal/` | The machinery: the claim-tree tool, the invariant checker, the ledger renderer, the task log. |
| `.claude/commands/` | The skills the agent used. |

## Licence

This repository is licensed under the GNU General Public License, version 3 or (at your
option) any later version (GPL-3.0-or-later; the text is in `LICENSE`), because it is a
modified version of GPL-3.0 work: an earlier version of
[`Laith-hk/AUTO-EWARS-csd`](https://github.com/Laith-hk/AUTO-EWARS-csd) (EWARS-csd), as
modified in [`chap-models/chapkit_ewars_model`](https://github.com/chap-models/chapkit_ewars_model).
`NOTICE` gives the line of descent and the copyright statement. Third-party material is not
covered by this licence: everything under `Archive/` keeps the terms it came with, stated
per directory in each `provenance.md`, and the example datasets are public data for which
this repository grants no licence.
