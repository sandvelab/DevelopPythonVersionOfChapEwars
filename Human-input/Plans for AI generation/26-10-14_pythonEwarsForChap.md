# Translate the CHAP-EWARS model from R to Python, run it through chap, veridically

The plan this repository exists to execute. It is written to be run by an agent that has
none of the planning conversation in context. Everything needed to start is either here or
retrieved in batch 1, which pins it under `Archive/`. Facts stated here about the external
repositories were read on 2026-10-14 through the GitHub API (`agent-retrieved`), not
recalled. Batch 1 re-verifies them against the pinned clones, and a mismatch is reported,
not patched over (§3).

---

## 1. The aim

**Build a Python version of the CHAP-EWARS model
(`chap-models/chapkit_ewars_model`, currently R-INLA + `dlnm`). It should give results
similar to the R original, run through chap exactly as the original does, and come with a
complete, explicit account of every judgment call and every obstacle met in the
translation.**

What is fixed and what is open:

1. **Fixed by this plan**
   - The model being translated is the one in `scripts/predict.R` and `scripts/lib.R` of
     `chapkit_ewars_model`, at the commit pinned in batch 1:
     - a negative-binomial likelihood with a `log(E)` population offset;
     - `f(ID_spat, model='iid', replicate=ID_year)`;
     - `f(ID_time_cyclic, model='rw1', cyclic=TRUE, scale.model=TRUE)`;
     - optionally a region-specific second cyclic RW1 (`region_seasonal`);
     - fixed effects on `dlnm::crossbasis` columns, built per covariate with
       `lag = c(1, n_lags)`, `argvar = ns` with `equalknots(x, 2)`,
       `arglag = ns` with `df = min(nlag, round(nlag/2)+2)` and `group = ID_spat`;
     - `control.fixed(prec.intercept = 1e-4, prec = precision)`;
     - 1000 posterior predictive samples per forecast row, drawn with `rnbinom(mu, size)`
       from `inla.posterior.sample`.
   - **`dlnmpy` (`Logic06183/dlnmpy`) replaces R `dlnm`** for the cross-basis (`human-set`).
   - The Python model is served as a **chapkit** service with the same contract as the
     original: the same input columns, the same config fields (`prediction_periods`,
     `n_lags`, `precision`, `region_seasonal`, `additional_continuous_covariates`), and
     the same output shape (`time_period, location, sample_0..sample_999`). chap-core then
     drives both models the same way (`human-set`).
   - Where a Python counterpart of an R function is missing or not trustworthy, **the R
     source is archived and a parallel Python version is written beside it**. That version
     is verified against R output before it is used (`human-set`).
2. **Judgment calls**: explored as alternatives nodes where they have plausible
   alternatives, logged otherwise. The foreseen ones are listed in §3. The largest is the
   **inference engine**: R-INLA has no established Python equivalent, so how the
   approximate Bayesian fit is reproduced is an open question with competing strategies
   (§4, *Inference*).

Two things are produced at once, and neither is subordinate to the other (`AGENTS.md` §1):

1. **A working Python model with a defensible fidelity score**: evidence on how close its
   forecasts are to the R original's, measured against how much the R original disagrees
   with *itself* across seeds, and how stable that closeness is across reasonable
   alternative translations.
2. **The complete veridical record of how it came about.** This includes the two
   documents the human asked for: the judgment-call list and the challenges overview (§4,
   *Deliverables*).

**The central comparison**: the Python model vs. the R original, on the same data, the
same chap backtest splits and the same config, through the same chap-core pipeline. The
yardstick is the R original's own seed-to-seed variability (its *noise floor*). A Python
model that scores well against the observed data but does not resemble the R model has not
answered the question. Neither has a Python model that resembles R on one dataset only.

## 2. What "similar results" means

The human expects similarity, not an exact match. This plan makes "similar" measurable at
five layers. Each layer isolates one source of discrepancy, so that a final difference can
be attributed to a cause rather than only observed:

| Layer | Compared | Expected agreement |
|---|---|---|
| L1 Data adapters | the derived model frame (`Cases`, `E`, `ID_spat`, `ID_year`, `ID_time_cyclic`, offsets from `lib.R`) | exact (identical values) |
| L2 Cross-basis | the `dlnmpy` matrices vs. R `dlnm` matrices on the same input, every config variant | ≤ 1e-8 absolute |
| L3 Posterior | the posterior mean and sd of fixed effects, random effects and hyperparameters (NB size, precisions) vs. INLA's, **on the R-built design matrix**, which separates the inference engine from L1–L2 | set from the noise floor (below) |
| L4 Predictive | per-row predictive quantiles (5/25/50/75/95 %) and mean, Python vs. R | relative to the R-vs-R noise floor |
| L5 chap | chap-core's evaluation metrics for both models on the identical backtest, plus the paired per-split difference | relative to the R-vs-R noise floor |

- **Primary**: L5. The chap backtest metric for the Python model minus that of the R model,
  per location and split, on the development data, set beside the same difference computed
  between two R runs with different seeds. The primary metric is chap's default
  probabilistic metric (CRPS if, as expected, chap reports it; batch 2 confirms what chap
  reports). "Similar" means the Python-vs-R difference is not systematically larger than
  the R-vs-R difference.
  - The numerical tolerance (for example "the median absolute difference is ≤ 2× the R
    noise floor") is **written to a file and committed in batch 5, before any Python
    prediction exists**. It is not chosen after the numbers have been seen.
- **Secondary**: L1–L4 as diagnostics, each with a file-grounded pass/fail. Also chap's
  naive baselines (whatever chap-core ships as the standard baselines; batch 2 identifies
  them), scored through the same pipeline. They put the R–Python gap in proportion: a gap
  much smaller than the gap between EWARS and a naive baseline is a gap that does not change
  any practical conclusion.

**The conclusion may be an uncertain call.** "The Python model is close at L1–L2, but L3
differs because no Python engine reproduces INLA's approximation, and the effect at L5 is
X" is a conclusion, and is reported plainly.

## 3. Non-negotiables

- **The holdout stays sealed until the final validation** (§4, *Held-out data*). The
  translation is developed and tuned only on the development data. The holdout is opened
  once, in a single batch, on a perturbation manifest frozen beforehand.
- **No number reaches a claim except through a file** (`AGENTS.md` §1). This includes the
  commands in the tutorial: they are the commands a script actually ran, and its log is
  stored.
- **The original is never modified.** The pinned clones under `Archive/` are read-only.
  Instrumentation of the R reference (extracting the derived frame, the cross-basis and the
  INLA posterior) is done by **separate R scripts in a node**, which source or copy-out the
  archived code. Every copy-out is recorded, and every difference from the archived code is
  a logged judgment call.
- **Every judgment call is a node or a logged decision, never silent**, and *in addition*
  carries an ID (`JC-NN`) in the judgment-call ledger (§4, *Deliverables*). Every obstacle
  carries an ID (`CH-NN`) in the challenge ledger. Foreseen calls, each to be resolved
  during execution:
  - inference engine (alternatives node, §4);
  - priors: reproducing INLA's *default* hyperpriors for `nbinomial`, `iid`, `rw1`. These
    are read from INLA's own documentation and source, never recalled;
  - the `scale.model=TRUE` scaling of the cyclic RW1 (porting `inla.scale.model`);
  - the RW1 sum-to-zero constraint and how replicated effects are indexed;
  - the NB parametrisation (INLA's `size` and its internal `log`-scale theta, vs. scipy's
    `n, p`);
  - the posterior sampling scheme (INLA's `inla.posterior.sample` from the Gaussian
    approximation and hyperparameter integration vs. MCMC draws or a Laplace grid);
  - the random-number generators (R `rnbinom` vs. numpy). Exact sample equality is not a
    goal, so how the seeds are matched is recorded;
  - `control.inla(strategy='adaptive')`: what of it is reproduced;
  - the R packages loaded but possibly unused (`sf`, `spdep`, `yaml`, `jsonlite`, `dplyr`);
    each is confirmed used or unused by reading the code;
  - the Python service design (chapkit runner type, Docker base image, how the config is
    passed);
  - any `dlnmpy` behaviour that differs from R `dlnm` on this model's specs.
- **Agency is recorded on every decision**: `human-set`, `agent-on-human-assessment` or
  `agent-autonomous`; for information, `agent-retrieved` or `human-pointed`.
- **Failures are kept.** An inference strategy that does not converge or does not match
  INLA stays in the tree, runnable, with its numbers.
- **If an anchor turns out to be wrong, stop and report it** rather than patch around it.
  Examples: the original does not run through chap as documented; `dlnmpy` disagrees with R
  `dlnm` beyond its documented precision; chap scores differently from its documentation.
  The obstacle becomes a `CH-NN` entry either way.

## 4. Decisions already made

| | Decision |
|---|---|
| **Evaluation platform** | **chap-core** (`dhis2-chap/chap-core`, default branch `master`, AGPL-3.0), pinned by commit in batch 1, with the **chapkit** library (`dhis2-chap/chapkit`, AGPL-3.0) pinned likewise. Documentation: https://chap.dhis2.org/ and the repos' `docs/`, archived as source material in batch 1. Both models are run through chap's evaluation command for chapkit services, which batch 2 identifies from the docs and verifies by running it. `human-pointed` (platform) / `agent-autonomous` (pinning). |
| **Metric** | chap-core's own evaluation output, written to file by chap. The primary metric is its CRPS (or its default probabilistic metric if that differs; recorded in batch 2). The L1–L4 comparison metrics are computed by node scripts and written to files. `agent-autonomous`. |
| **Backtest scheme** | chap-core's backtest as invoked by its evaluate command, with the **identical** settings for R and Python (number of test splits, prediction length = `prediction_periods`). The exact settings are recorded as a file in batch 2 and never changed afterwards without a §4b entry. `agent-autonomous`. |
| **Required baselines** | the naive or standard baselines chap-core ships (identified in batch 2), through the same pipeline. `agent-autonomous`. |
| **Reference model** | **the R original**: `chap-models/chapkit_ewars_model` (GPL-3.0). It runs as its GHCR image pinned by **digest**, and also as a local Docker build from the pinned clone if the image digest cannot be tied to the pinned commit. R-INLA is amd64-only, so on Apple Silicon it runs under emulation; the slowness is recorded, not avoided. `human-pointed`. |
| **Modelling resources** | `dlnmpy` (`Logic06183/dlnmpy`, GPL-2.0-or-later) pinned by commit and PyPI version, archived. The R sources of `dlnm` and of the R-INLA functions this model relies on (at least `inla.scale.model`, the cyclic-`rw1` and `iid` model definitions, the `nbinomial` likelihood and prior documentation, `inla.posterior.sample`) are archived under `Archive/r-sources/` with their versions as found **inside the reference Docker image**, so that they are the versions the reference actually ran. They are used as design and as test oracles; Python ports live in node scripts. `human-pointed` (dlnmpy) / `agent-autonomous` (the rest). |
| **Data** | **Development**: the two example datasets shipped in `chapkit_ewars_model`: `example_data_monthly/` (monthly) and `example_data/` (weekly), so that both the monthly and the weekly code paths are developed. Archived at the pinned commit with `sha256sums.txt`; licence as the repo's (GPL-3.0), confirmed in batch 1. `agent-autonomous`; **open question Q1**. |
| **Target** | `disease_cases` per `location` per `time_period`, as 1000 predictive samples per row, at the dataset's resolution (week or month). |
| **Held-out data** | **One or two datasets from chap-core's `example_data/`** not used in development. They are selected in batch 1 **by file name, size and row count only** (one monthly, and one weekly if available, with the columns the model needs), checksummed and sealed under `Archive/holdout/`. They are not opened, plotted or summarised beyond row counts and completeness until phase E. `agent-autonomous`; **open question Q1**. |
| **Project seed** | `20261014`. Every component seed derives from it per `AI-internal/skill-references/provenance-record.md`. The R reference gets its seeds the same way: an R `set.seed` and INLA's `seed` argument in the instrumentation scripts, and for chap runs whatever seeding chap and the image allow, recorded in batch 2. `agent-autonomous`. |
| **Environment** | Main: Python 3.13 (the chapkit model template requires ≥3.13 and dlnmpy supports 3.13), with numpy, scipy, pandas, statsmodels, dlnmpy, the inference library or libraries the candidates need, chapkit and chap-core. Pinned by `/pin-environment` once batch 3's inventory is known. **Docker: yes.** The R reference is a Docker image, and the Python model ships its own image so that chap drives both identically. The R instrumentation scripts run inside the reference image (a node-level `env/`, justified in that node's `claim.md`). `agent-autonomous`. |
| **Inference** (the main open judgment call) | An alternatives node, every candidate fitting the *same* model to the *same* design matrix: **a)** a Laplace / INLA-style approximation written in Python (a Gaussian approximation of the latent field given the hyperparameters, with integration over a hyperparameter grid). This is the closest in method to the original. **b)** full MCMC (e.g. NumPyro NUTS or PyMC) on the same model and priors. This is exact Bayes, so where it differs from INLA the difference is INLA's approximation. **c)** an existing Python INLA implementation, *if* batch 3's reconnaissance finds a credible one. Calling R-INLA from Python (rpy2) is **recorded as rejected**, because it would not be a Python version. The main path is chosen on development L3–L5 fidelity, then cost. The rejected candidates stay runnable. `agent-autonomous`. |
| **Deliverables** | (1) **Tutorial**: `AI-generated/26-10-14_tutorialRunOriginalEwarsThroughChap.md`. The exact commands, from a fresh terminal, to clone and install chap-core, start the original EWARS service and evaluate it through chap. Each command is taken from a script that ran it, with its log stored. A second section, for the Python model, is added in phase C. (2) **Judgment-call list**: `AI-generated/translation-record/judgment-calls.md`. (3) **Challenges overview**: `AI-generated/translation-record/challenges.md`. (2) and (3) are rendered by a script (`AI-internal/useful-scripts/render_translation_record.py`) from the structured ledgers `AI-internal/translation-log/judgment_calls.yaml` and `challenges.yaml`, which are appended to as the work happens and never edited retroactively. Each rendered file opens with a **short main part**: one line per entry, with the ID, the call or challenge, and the choice or solution in a few words. All further detail goes to an **appendix at the end**: alternatives considered, basis, agency, the node or result it links to, and whether the stability run showed it matters. `human-set` (content and shape) / `agent-autonomous` (locations, mechanism). |
| **Tracking level** | **standard** (`AGENTS.md` §6): every result gets provenance, and the stability work is cut at the compute budget. Raise it with the human if the L3 fidelity question turns out to be the article's real contribution. `agent-autonomous`. |
| **Compute budget for stability** | Set in phase D, once the per-run cost of the emulated R reference and of each inference candidate is known. `agent-autonomous`. |
| **Storage budget** | Not a constraint, except that cloned repositories and Docker images are archived by commit and digest, with the clones gitignored if over ~50 MB. In that case they are re-obtainable from `provenance.md`, and the decision is logged. `agent-autonomous`. |
| **Data governance** | Public example data from GPL/AGPL repositories; redistributable under their licences, confirmed in batch 1. The release carries the licences of everything archived. |
| **Scope of the tree** | The whole analysis is in `analysis/`. The Python chapkit service (its `main.py`, `pyproject.toml`, `Dockerfile` and model package) lives in a node's `scripts/`. Whether it is later split out into its own repository is **open question Q3**. |
| **Git remote** | `sandvelab/DevelopPythonVersionOfChapEwars`, public, created 2026-10-14. Commit per `/commit-run`. Nothing is pushed without the human's instruction. `/release` runs the secrets and data-permission scan first. `human-set`. |

### Open questions for the human

Each has a default, so execution does not stall; the human may override any of them before
or during the run.

- **Q1: data.** The default is to develop on the EWARS repo's weekly and monthly examples,
  with the holdout from chap-core's `example_data/`. Is there a real dataset (e.g. a
  country's DHIS2 export) that should be the holdout instead?
- **Q2: tolerance.** The default "similar" threshold is set from the R noise floor in batch
  5, before the Python results are seen. Does the human want a stricter or a looser bar, or
  specific quantities that must match?
- **Q3: packaging.** The default is for the Python service to live in the tree, with a
  later split into e.g. `chap-models/chapkit_ewars_model_python` only on the human's
  instruction.

## 4b. Decisions settled during execution

Append-only, oldest first.

### 2026-10-14 — repository remote (outside the plan)

| Decision | Basis | Agency |
|---|---|---|
| `origin` repointed from `sandvelab/agentic-model-development-start` to `sandvelab/DevelopPythonVersionOfChapEwars`; repo created public; `main` pushed; local `old-history` branch not pushed | the human's instruction | human-set |

### 2026-10-14 — batch 1: anchors, data partition, ledgers

| Decision | Basis | Agency |
|---|---|---|
| Pinned commits: chapkit_ewars_model `964eea8bfdb194ca8985723216e94f1ac63aa4f1`, chap-core `b8c8f788fbc011f3d9d8a18ba9e993725023a6e4`, chapkit `b8ccd072cbf0d4c70fa34f8e818551ca5937aa75`, dlnmpy `8c5edd79ea989d22b457bfb93e03b0c5e125792c` | the HEAD of each default branch on 2026-10-14, cloned by `AI-internal/data-acquisition/fetch_repos.sh` | agent-autonomous; information: human-pointed |
| The chap documentation is archived as part of the chap-core clone (`Archive/chap-core/src/docs/`, the mkdocs source of chap.dhis2.org) rather than scraped from the website | the same text, pinned by commit; the website is built from it | agent-autonomous |
| **Data selection differs from the §4 default** (JC-01): development is the EWARS monthly example plus Nicaragua weekly before 2018-01-01; the holdout is the Laos monthly subset plus Nicaragua weekly targets from 2018-01-01. The EWARS `example_data/` is a smoke test only | the default's weekly development set has 8 periods (CH-01), so the weekly path would first meet real data at the holdout | agent-autonomous; information: agent-retrieved |
| Translation ledgers are JSON (`judgment_calls.json`, `challenges.json`), not the YAML §4 names | the repository machinery is standard-library only (`setup-guide.md` §3), and Python's standard library has no YAML parser | agent-autonomous |
| `.claude/settings.json` placeholders filled in; the excludes also cover `~/ai/CLAUDE.md` | setup-guide §2; that grandparent `CLAUDE.md` was observed to load into this project's sessions, which would silently change the method | agent-autonomous |
| `Archive/chap-core/src/` is gitignored (65 MB, CH-04) | plan §4 storage rule | agent-autonomous |

### 2026-10-14 — batch 2: the R reference through chap

| Decision | Basis | Agency |
|---|---|---|
| Backtest settings for every chap evaluation: `n_periods 3`, `n_splits 7`, `stride 1`, `future_weather_provider climatology`, in `analysis/01_referenceThroughChap/scripts/backtest_settings.env` (JC-02, JC-04) | chap eval's defaults; n_periods = EWARS's default `prediction_periods`; climatology is chap's default and forecasts the covariates of each window rather than passing the observations | agent-autonomous; information: agent-retrieved |
| **Primary metric is chap's `crps`** (from `chap export-metrics`); chap also reports crps_log1p, crps_norm, mae, rmse, coverage_10_90/25_75, winkler scores and others | `results/run1/metrics/*.csv` | agent-autonomous |
| **Baselines are chap-core's three built-in role-baseline models**: `builtin:global_median`, `builtin:seasonal_median`, `builtin:persistence` (JC-07) | `chap_core/models/builtin/` | agent-autonomous; information: agent-retrieved |
| R reference image pinned: `ghcr.io/chap-models/chapkit_ewars_model@sha256:959fb4f0f1b9d257a9697925f4500fd8ec4ffa9e1bb3ed7fc36e4f5c57c6ff88` (tag `sha-964eea8`; reports git_revision 964eea8b); no local build needed (JC-08) | publish workflow's sha tags; `/api/v1/info` | agent-autonomous |
| chap-core installed from the pinned commit with `uv sync --frozen`, not `uv tool install` (JC-03) | the docs' route installs the latest release with unpinned dependencies | agent-autonomous |
| **Model inputs are the development files reduced to the six-column chap data contract** (JC-05) | the monthly example file as shipped makes the R original fail through chap (CH-07); the contract is the README's | agent-autonomous; information: agent-retrieved |
| Seeding: none possible at chap level for the R model (CH-10); the L5 noise floor comes from repeated unseeded chap runs | no `set.seed` in the R scripts, no seed field in the config | agent-autonomous |

### 2026-10-14 — batch 3: translation inventory

| Decision | Basis | Agency |
|---|---|---|
| The inventory is the parser's list of every call (171 sites, 65 distinct, formula terms included) joined to an authored mapping; a script fails if any call is unmapped (JC-09) | `analysis/02_translationInventory/` | agent-autonomous |
| **Inference candidate (c) does not exist in usable form** (JC-10): pyINLA rejected (wraps INLA's own engine; proprietary licence; no Python 3.13 wheel); pylgm (MIT) lacks cyclic RW1, replicate and INLA's priors, and is noted as a possible building block for candidate (a), decided in batch 8. Batches 8–10 therefore build (a) and (b) | `Archive/python-inla-candidates/` | agent-autonomous; information: agent-retrieved |
| **The port reproduces the R code's quirks** rather than correcting them (week-53 fold, NA-case rows predicted, NA basis rows as 0) (JC-11) | plan §1: the model being translated is predict.R/lib.R | agent-autonomous |
| **Main environment pinned now** with numpy, scipy, pandas, pyyaml, dlnmpy @ 8c5edd79; inference libraries added when the candidates are built (JC-12) | `environment/README.md` | agent-autonomous |
| **Every candidate reproduces the model exactly** (likelihood, the installed INLA's default priors, constraints, NA-as-0); INLA's engine settings are candidate-specific and recorded per candidate (JC-13) | `results/inla_defaults.tsv` | agent-autonomous |
| R-INLA and dlnm sources archived from the versions in the image: r-inla tag `Version_25.10.19` (commit acb55f37), dlnm 2.4.10 from CRAN, and the image's installed code and defaults | `Archive/r-sources/` | agent-autonomous; information: agent-retrieved |

### 2026-10-15 — batch 4: R reference harness

| Decision | Basis | Agency |
|---|---|---|
| The harness fits one window per development dataset: the final 3 periods, with observed covariates, in the file shape chap hands the model (JC-14) | the weekly history equals chap's own workspace file value for value | agent-autonomous; information: agent-retrieved |
| predict.R is instrumented by inserting taps into its parsed body, not by a copy-out; the only changed statement seeds the sampler (JC-15, JC-16) | `instrumentation.txt` in every run directory | agent-autonomous |
| Seed derivation rule: 1 + sha256("20261014/<component>")[:4] mod (2^31 − 2) (JC-17) | `derive_seeds.py`; stated in readme-at-start.md | agent-autonomous |
| Per-row files of replicates 2–5 are gitignored, with a sha256 manifest (JC-18) | 168 MB of results | agent-autonomous |
| L5 noise floor: 4 unseeded chap repeats per dataset, EWARS only (JC-19) | CH-10 | agent-autonomous |
| **A single-threaded diagnostic was added to the batch** (3 fits per dataset) after refits of identical inputs disagreed | tests the obvious cause of CH-20; it did not explain it | agent-autonomous |
| **Batch 5 waits for the human** (plan §3, stop and report): the R reference's INLA fit is not reproducible and occasionally degenerates or crashes (CH-20), so how R-vs-R tolerances treat a degenerate R fit is a decision, not a default | `analysis/03_referenceHarness/claim.md` answers 3–5 | agent-autonomous (to stop); the decision itself is the human's |

### 2026-10-17 — the human's answer to CH-20, and a runnable model first

| Decision | Basis | Agency |
|---|---|---|
| **No tolerance file and no automatic pass/fail at any layer.** This replaces §2's file-grounded pass/fail and batch 5's tolerance file, and answers Q2. The fidelity output is a report of how close the Python model's behaviour is to the R reference's, layer by layer | the human: "No automatic pass/fail - just give me a report of how close the behavior is" | human-set |
| **The R reference counts as it runs** (reading 1 of the batch 4 report). Degenerate fits and crashes are not excluded. They are counted and their behaviour is summarised beside the healthy fits, and the human applies the yardstick | the human: "count and show summaries of behavior. I can manually apply a yardstick" | human-set |
| **A chap-compatible Python EWARS model in a folder the human can run, with a short guide to running it** | the human's request | human-set |
| The folder is the chapkit service package in the tree (Q3's default), at `analysis/05_pythonModel/scripts/chapkit_ewars_python/`. Every node that tests the Python model imports this package, so the code tested at L1–L4 is the code chap runs (JC-20) | Q3 default; one copy of the model code | agent-on-human-assessment |
| **Order: batches 5–8 (candidate a), then 11, before 9** (candidate b, MCMC). The runnable model comes first; candidate b stays open in the ledger | the human asked for a runnable model; candidate (a) is the one closest in method to INLA (§4, *Inference*) | agent-autonomous |

## 5. How this plan is used

`/do` runs the next open batch of §6 and stops. Sketched phases become concrete batches as
they are reached. Before batch 1 runs, the plan as it stands is archived to
`Archive/plan-as-delivered/`. Every batch appends to the two translation ledgers whenever
it makes a call or meets an obstacle, and re-renders the two documents at its end.

## 6. Batch ledger

| Batch | Phase | Aim | Status |
|---|---|---|---|
| 0 | — (outside the plan) | Repoint the git remote and create the public GitHub repository (§4b). | done |
| 1 | A — Orient & set up | Read `readme-at-start.md`, `AGENTS.md`, `MOTIVATION.md`. Archive this plan to `Archive/plan-as-delivered/`. **Clone chap-core, chapkit_ewars_model, chapkit and dlnmpy** with a fetch script in `AI-internal/data-acquisition/`; record each commit, and archive them under `Archive/` with `provenance.md` (`IS_SHADOW`) and checksums. If a clone fails, that is the batch's finding (`CH-01`…). Archive the chap documentation pages needed (evaluating a chapkit model, the CLI) as source material. Archive the development data; select and seal the holdout (§4). Create the two translation ledgers and the renderer. Fill in `readme-at-start.md` from this plan, and write the root `analysis/claim.md`. Re-verify the §4 facts about the R code against the pinned clone. No modelling. | done |
| 2 | B — Reference through chap + tutorial | Find from the archived docs how chap-core evaluates a chapkit service. Script it from a *fresh shell* (no inherited env): install chap-core per its docs (uv), start the original EWARS service (pinned image), run chap's evaluation on the development data with the backtest settings fixed here and written to file, and capture every command and its output. Produce the R reference's first file-grounded chap scores, plus the chap baselines through the same pipeline. Write the **tutorial** from the script and its log. A second clean-shell run of the tutorial's commands, diffed, confirms they are complete. | done |
| 3 | B — Translation inventory | Read `predict.R`, `lib.R`, `train.R` and `main.py` in full. Produce a file mapping **every R call** to its Python counterpart or a gap (dplyr→pandas; `crossbasis`/`equalknots`→dlnmpy; `inla`, `f(...)`, `inla.posterior.sample`, `rnbinom`→?). Retrieve INLA's default hyperpriors and parametrisations from the INLA documentation and source inside the reference image, and archive them. Search for existing Python INLA implementations and assess any that exist. Archive the R sources needing parallel ports. Seed the JC and CH ledgers with what this inventory reveals. | done |
| 4 | B — Reference harness | An R instrumentation node, run inside the reference image, that emits for each development dataset × config variant (defaults; `region_seasonal=true`; `n_lags=[3,6]`; covariates `[]`): the L1 derived frame, the L2 cross-basis matrices, the L3 INLA posterior summaries, and the L4 predictive samples, each **for at least 5 seeds**, to measure the R noise floor at L3–L5. Also run 2+ chap evaluations of the R model with different seeds for the L5 noise floor. | done — **stopped for the human: CH-20** |
| 5 | B — Fidelity metrics | Scripts computing L1–L5 comparisons from files, with no pass/fail (§4b, 2026-10-17). Run them R-vs-R to describe the reference's own behaviour as it runs, degenerate fits and crashes counted rather than excluded. | open |
| 6 | C — Data layer + cross-basis | A Python port of the adapters and `lib.R` offsets (L1 exact), and the cross-basis via `dlnmpy` (L2 ≤1e-8) on every variant. Any `dlnmpy` gap is ported in parallel from the archived R `dlnm` source and tested against R, and logged as a CH entry. | open |
| 7 | C — Model primitives | Python ports of the INLA pieces common to all candidates: the cyclic RW1 structure matrix and `inla.scale.model` scaling, the constraints, iid with replicate, the NB likelihood in INLA's parametrisation, and the default priors. Each is checked against the archived R/INLA values. | open |
| 8–10 | C — Inference candidates | One candidate per batch (§4, *Inference*: a, b, c if it exists) as alternatives children, each scored at L3 and L4 against the R reference on the R design matrix and on the Python design matrix. Record cost and convergence. Then the **main-path decision** on development evidence, with the rejected candidates kept runnable. | open |
| 11 | C — chapkit service | Package the main-path model as a chapkit service mirroring the original `main.py` (the same id scheme with a `-python` suffix, the same config schema and output) with its own Docker image. Run it through chap with the batch-2 backtest. L5 against R and the baselines. Add the Python section to the tutorial. | open |
| | D — Stability | A perturbation manifest from the JC ledger (the inference candidates, prior interpretations, sample count, seeds, config variants, any approximation settings), costed. Set the budget, freeze, run, and report the distribution of the L5 Python–R gap, not the single number. Mark in the JC ledger which calls move the conclusion. Freeze the holdout manifest. | open |
| | E — Final validation | Open the holdout once; run the frozen manifest for both R and Python through chap; report the held-out fidelity distribution beside the development one. | open |
| | F — Claims & report | The claim collection from the tree; the hierarchical report; the final render of the judgment-call list and the challenges overview (short main part, details in the appendix). | open |
| | F (cont.) | `/validate cleanroom` and `/validate outsider`; fix what they find. | open |
| | F — Release | The manuscript section(s) the results support; the release scan; push on the human's instruction. | open |

## Batch ledger — reports

*(One link per completed batch, added by `/do`. Never overwritten.)*

- Batch 1 — [[26-10-14_b01_orientAndSetUp]]
- Batch 2 — [[26-10-14_b02_referenceThroughChap]]
- Batch 3 — [[26-10-14_b03_translationInventory]]
- Batch 4 — [[26-10-15_b04_referenceHarness]]
