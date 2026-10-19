# Read this first

The first thing to read in a new session, human or agent. It says what *this particular*
project is. When it stops matching reality it is worse than nothing.

Then read `AGENTS.md` — the standing instructions, and the single source of truth for how
work is done here.

---

## The project

**Translate the CHAP-EWARS disease-forecasting model (`chap-models/chapkit_ewars_model`,
R-INLA + `dlnm`) into Python, with `dlnmpy` in place of `dlnm`, run it through chap-core as a
chapkit service, and establish how close its forecasts are to the R original's, measured
against the R original's own seed-to-seed variability.** Full aim, success criteria and
non-negotiables: `Human-input/Plans for AI generation/26-10-14_pythonEwarsForChap.md`.

## Where the project starts from

| Anchor | This project |
|---|---|
| Evaluation platform or harness | chap-core @ `b8c8f788` with chapkit @ `b8ccd072`, at `Archive/chap-core/`, `Archive/chapkit/` |
| Metric | chap-core's `crps` from `chap export-metrics` (confirmed in batch 2); secondary: fidelity layers L1–L4 (plan §2) |
| Backtest or split scheme | `chap eval` rolling-origin backtest: 7 splits, 3-period horizon, stride 1, `climatology` future weather; `analysis/01_referenceThroughChap/scripts/backtest_settings.env` |
| Required baselines | chap-core's built-in `global_median`, `seasonal_median`, `persistence` |
| Reference model | the R original, chapkit_ewars_model @ `964eea8b`, run as `ghcr.io/chap-models/chapkit_ewars_model@sha256:959fb4f0…c6ff88` (linux/amd64); given the development files reduced to the six-column data contract (JC-05) |
| Modelling resources to start from | dlnmpy @ `8c5edd79` at `Archive/dlnmpy/`; R-INLA 25.10.19 (tag commit `acb55f37`) and dlnm 2.4.10 sources, plus the reference image's installed code and defaults, at `Archive/r-sources/` |
| Data | EWARS repo and chap-core example data, at `Archive/dev-data/` and `Archive/holdout/` with `sha256sums.txt`; licence: that of the shipping repositories (CH-03) |
| Target | `disease_cases` per location per period (week or month), as 1000 predictive samples per row |
| Development data | `Archive/dev-data/`: EWARS monthly example (23 locations, cases 2001-01..2016-12, plus a covariate-only future file to 2017-06); Nicaragua weekly, periods before 2018-01-01 |
| Held-out data | `Archive/holdout/`, sealed: Laos monthly subset (3 locations); Nicaragua weekly targets from 2018-01-01 |

## The article

- **Target venue**: not yet decided.
- **Status**: batches 1–11 done; inference candidate (a) is the main path, and candidate (b),
  NUTS on the same density, gives the same forecasts (`analysis/05_pythonModel/03_inference/`). The Python model is a
  chapkit service at `analysis/05_pythonModel/scripts/chapkit_ewars_python/` (run guide in its
  `README.md`), evaluated through chap like the R original. The closeness report is
  `analysis/06_closenessReport/results/closeness_report.md`. It applies no pass/fail: the human
  applies the yardstick, and the R reference counts as it runs (plan §4b, 2026-10-17). Open:
  phase D (stability), phase E (holdout).
- **Manuscript**: `Human-AI-collaboration/manuscript/` (empty).
- **The plan being executed**: `Human-input/Plans for AI generation/26-10-14_pythonEwarsForChap.md`.
  It carries the batch ledger (§6); `/do` runs the next open batch and stops.

## Settings this project has fixed

| Setting | Value |
|---|---|
| Project random seed | `20261014`. Component seed = 1 + (first 4 bytes of sha256(`"20261014/<component>"`), big-endian) mod (2³¹ − 2), so it is valid for R, INLA and numpy (JC-17; first used in `analysis/03_referenceHarness/scripts/derive_seeds.py`). |
| Main environment | Python 3.13.0 with numpy, scipy, pandas, pyyaml and dlnmpy @ `8c5edd79`, pinned in batch 3; numpyro 0.22.0 (jax 0.11.2) added in batch 9 for candidate (b). Installed from `environment/lock.txt` by `environment/install-env.sh`. Invoked as `environment/env/bin/python`. Docker image: yes — the R reference is one, and the Python model ships one so chap drives both identically. |
| Repository machinery interpreter | `.venv`, per `setup-guide.md` §3. |
| Tracking level | standard (`AGENTS.md` §6). |
| Compute budget for stability work | not yet set — set in phase D; measured per-run costs: Python fit 1–11 s, Python chap evaluation 2–6 min, R chap evaluation 4–7 min |
| Storage budget | not a constraint; clones over ~50 MB gitignored and re-obtainable by commit |
| Data governance | public example data, redistributable under the shipping repositories' licences (re-checked at release) |
| Git remote | `sandvelab/DevelopPythonVersionOfChapEwars`, public. Nothing is pushed without the human's instruction; `/release` runs the secrets and data-permission scan before anything becomes public. |

## What must not happen

These override everything else here; the plan's §3 states them in full for this project.

1. **The holdout is sealed before any work begins and opened once**, at the final validation,
   across a perturbation manifest frozen beforehand. Nothing is added, dropped, re-tuned or
   re-run on the holdout after a number from it has been seen.
2. **No number reaches a claim except through a file.** Whatever computes a score writes it
   to a file; every reported figure is read from that file by a script.
3. **Every judgment call is a node or a logged decision, never silent**, and carries a
   `JC-NN` id in `AI-internal/translation-log/judgment_calls.json`; every obstacle a `CH-NN`
   id in `challenges.json`.
4. **Agency is recorded on every decision.**
5. **Failures are kept**: an inference strategy that does not converge or does not match
   INLA stays in the record, runnable.
6. **The original R model is never modified**; it is instrumented by separate scripts.
