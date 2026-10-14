# Batch 2 — The R reference through chap, and the tutorial

Generated from [[26-10-14_pythonEwarsForChap]] — batch 2 (phase B).

Node: `analysis/01_referenceThroughChap/`. Every number below is read from a file in its
`results/`, named beside the number.

## What was done

- **How chap evaluates a chapkit service was taken from the archived docs and source.**
  The sources were `docs/chap-cli/eval-reference.md` and
  `chap_core/cli_endpoints/evaluate.py`. The R original runs as a running service, given
  as `--model-name http://localhost:8000 --run-config.is-chapkit-model`.
- **Everything ran from a fresh shell** (`env -i`, no profile), through the node's
  `run.sh`:
  - chap-core cloned at `b8c8f788` and installed from its own lockfile (JC-03);
  - the EWARS image started by digest; the service reports git revision `964eea8b`
    (`results/run1/service_info.json`, JC-08);
  - one `chap eval` per dataset and model: EWARS and the three built-in baselines, all on
    the same backtest settings;
  - `chap export-metrics` per dataset.

  Every command and its output is in `results/run1/run.log`.
- **The backtest settings are a file**: `scripts/backtest_settings.env`. They are 7 splits,
  a 3-period horizon, stride 1, and the `climatology` future-weather provider (JC-02,
  JC-04). In a backtest, chap gives a model forecast covariates for each window rather than
  the observed ones. R and Python will see the same forecasts.
- **What chap reports**: `crps` is the primary metric. Alongside it come crps_log1p,
  crps_norm, mae, mape, rmse, coverage_10_90 and coverage_25_75, Winkler scores, and
  outbreak sensitivity/specificity (`results/run1/metrics/`).
- **The baselines are chap-core's three built-in role-baseline models**: global_median,
  seasonal_median and persistence (JC-07).
- **The tutorial was written from the script and checked.**
  `AI-generated/26-10-14_tutorialRunOriginalEwarsThroughChap.md` uses the EWARS repo's own
  monthly example. `scripts/verify_tutorial.sh` extracted its `bash` blocks and ran them
  verbatim in an empty shell. Every check passed (`results/tutorial_check/verdict.txt`):
  - the tutorial exits 0;
  - its input is byte-identical to run1's;
  - its seasonal_median scores equal run1's on every metric;
  - its EWARS evaluation produced scores.

## The R original's first chap scores

From `results/run1/reference_scores.tsv`. CRPS, lower is better; wall-clock seconds for the
whole 7-split evaluation under amd64 emulation:

| Dataset | EWARS (R) | global_median | seasonal_median | persistence | EWARS seconds |
|---|---|---|---|---|---|
| monthly (23 states) | 1129.1 | 1129.7 | 740.7 | 822.5 | 193 |
| weekly (Nicaragua, 10 departments) | 22.10 | 30.54 | 31.65 | 11.21 | 267 |

On monthly data, the R original does no better than the global median and worse than the
other two baselines. On weekly data it beats both medians, and persistence beats it.
These are the settings' first scores, not yet set against the R noise floor (batch 4).

## What went wrong, and what it showed

- **The R original fails on its own monthly example when chap backtests it (CH-07).**
  INLA stops with "Locations are too close for f(ID_time_cyclic, model="rw1")".
  - **Diagnosis.** The failed predict job's workspace was downloaded through chapkit's
    artifact API (`results/diagnose_monthly/workspace_inspection.txt`).
  - **Cause.** The example file carries columns that `predict.R` would otherwise derive
    itself, `month` among them. chap's climatology provider forecasts every non-target
    column for the forecast window, so `month` reached R as `10.00000000000001`,
    `10.999999999999986` and `12.000000000000018`. `predict.R` uses an existing `month`
    column as it is.
  - **Fix.** The same file reduced to the README's six-column data contract runs
    (`results/diagnose_monthly/outcomes.txt`). Every development file is now reduced to
    the contract before evaluation (JC-05).
  - **Not an anchor failure.** The model runs through chap on data shaped as its README
    specifies.
  - The evaluation of the files as archived is kept in
    `results/run1_attempt2_archivedInputs/`.
- **The R reference cannot be seeded through chap (CH-10).** `predict.R` sets no seed, and
  the config has no seed field. Two independent monthly runs gave EWARS CRPS 1129.1 and
  1125.7 (`results/tutorial_check/verdict.txt`). The L5 noise floor in batch 4 therefore
  comes from repeated unseeded runs.
- **chap sends an empty covariate list when a config YAML omits it (CH-08).** The model then
  runs without its climate covariates and nothing warns. Found by reading the source before
  any run. The config file states the covariates (JC-06).
- **The first run stopped at the first failed evaluation (CH-09).** macOS's bash 3.2 exited
  under `set -e` because of a command substitution in `PS4`. Fixed; that run's outputs are
  kept in `results/run1_attempt1_aborted/`.
- **Weekly periods reach the model as `2004-W01` (CH-06 resolved in CH-12)**, which
  `predict.R` parses as intended (`results/run1/weekly_workspace/inspection.txt`).
- **Two weekly behaviours for batch 3 to settle (CH-13).**
  - R predicts every row with missing cases, not only the future window; chap discards the
    extra rows.
  - `lib.R`'s `%% 52` puts ISO week 53, present in the data, on the cyclic index of
    another week.

## Ledgers

JC-02 to JC-08 and CH-07 to CH-13 were added. CH-11 records the resolution of CH-02
(Docker), because the ledgers are append-only. The rendered documents are
`AI-generated/translation-record/judgment-calls.md` and `challenges.md`.

## For the human

1. **The input reduction (JC-05) was decided without you.** The alternative is to treat the
   failing monthly example as a stop-and-report anchor failure. It was not treated as one,
   because the README's data contract is met, but you may see it differently.
2. **Climatology weather (JC-04)** means the backtest scores include chap's weather-forecast
   error. For fidelity this is neutral, because R and Python get the same covariates.
   `observed` weather would isolate the models, and is a candidate perturbation for phase D.
3. Q1–Q3 in plan §4 still stand with their defaults.

## Next

Batch 3: the translation inventory. It reads `predict.R`, `lib.R`, `train.R` and `main.py`
in full, maps every R call to Python, and resolves CH-05 and CH-13.
