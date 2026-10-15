# Batch 4 — The R reference harness

Generated from [[26-10-14_pythonEwarsForChap]] — batch 4 (phase B).

Node: `analysis/03_referenceHarness/`. Every number below is read from a file in its
`results/`, named beside the number.

## What was done

- **The R reference was instrumented without modifying it** (JC-16).
  `scripts/instrument_reference.R` runs inside the pinned reference image. It works as
  follows:
  - it evaluates the archived `predict.R` verbatim, up to its command-line block;
  - it builds an instrumented `predict_chap` from the function's own parsed body;
  - it inserts tap calls between statements, which it locates by their exact text;
  - it changes exactly one statement: the posterior sampler receives a seed, preceded by
    `set.seed` (JC-15).

  Every run directory carries `instrumentation.txt`, which lists the changes, and the
  instrumented function itself.
- **The taps write each fidelity layer to file** for every fit:

  | Layer | Files |
  |---|---|
  | L1–L2 | `model_frame.csv.gz` (the frame passed to `inla()`, basis columns included), `formula.txt`, `crossbasis.json` (knots, boundary knots, lag df) |
  | L3 | `fixed.csv`, `hyperpar.csv`, `random_<term>.csv`, `linear_predictor.csv.gz`, `fitted_values.csv.gz`, `configs.csv` (the integration points), `fit_info.json` |
  | L4 | `posterior_draws.csv.gz` (size and `Predictor` per draw), `hyperpar_draws.csv`, `predictions.csv.gz` (predict.R's own output) |
- **The inputs are one window per development dataset** (JC-14).
  - The future is the final 3 periods of every location, with observed covariates.
  - The history and file shape are those chap hands the model. The weekly history equals
    chap's own workspace file, value for value.
- **The sweep:**
  - 2 datasets × 4 config variants (default; `region_seasonal`; `n_lags` [3, 6]; no
    covariates) × 5 seeded replicates, plus a repeat of replicate 1 with the same seeds.
    That is 42 fits, all exiting 0 (`results/fit_summary.tsv`).
  - Seeds derive from the project seed by a fixed hash rule (JC-17, `results/seeds.tsv`).
- **The L5 noise floor:** the R original was evaluated through chap 4 more times per
  dataset, unchanged from batch 2 and unseeded (CH-10, JC-19).
- **A diagnostic:** the default config was fitted 3 times per dataset with INLA restricted to
  one thread (`results/thread_diagnostic/`).

## What the harness shows

- **L1 and L2 are deterministic.** The model frame, basis and formula are identical in every
  refit (`results/refit_agreement.tsv`). They are a fixed target for the Python data layer.
- **INLA's `Predictor` includes the log(E) offset** (CH-22, resolving CH-19).
  - Rebuild the linear predictor from one posterior draw's components, and the remainder is
    log(E), to at most 1.2e-14 in all 47 completed fits (`results/fit_summary.tsv`).
  - The same check confirms the replicate indexing of both replicated terms, and that
    missing basis values enter as 0.
- **INLA resolved `int.strategy auto` to a central composite design:** 15 integration
  points with three hyperparameters, 25 with four. The fits ran in `compact` mode with 8:1
  threads.

## The R reference's fit is not reproducible (CH-20)

With nothing changed between runs (the same image, input bytes and seeds), the INLA fit
gives different posteriors.

- **The hyperparameter modes move between refits**, most of all the cyclic-RW1 precision
  (`results/fit_summary.tsv`, replicates 1–5):

  | Dataset | Variant | log size (mode) | RW1 log precision (mode) |
  |---|---|---|---|
  | monthly | default | 0.649–0.664 | 1.77–2.04 |
  | monthly | no covariates | 0.595–0.597 | 1.43–1.70 |
  | monthly | region_seasonal | 1.069–1.071 | 1.97–2.33 |
  | weekly | default | 0.6807–0.6811 | 2.75–2.78 |
  | weekly | nlags [3, 6] | 0.682–0.684 | 2.65–2.85 |

  Monthly fitted values differ by up to 472 cases between refits; weekly by up to 8
  (`results/refit_agreement.tsv`).
- **One of the 42 sweep fits converged to a degenerate mode**: monthly, default, the seeded
  repeat (`results/seeded_repeat.tsv`).
  - Posterior mean NB size 1.34 and iid precision 290, against 1.91 and 0.64 for
    replicate 1 (each run's `hyperpar.csv`).
  - 4 integration points instead of 15.
  - Six "vb.correction aborted" warnings in its log.
  - INLA nevertheless reported `mode_status` 0.
- **Threading is not the cause.** Single-threaded fits also differ from one another
  (`results/thread_diagnostic.tsv`). On weekly data, one of the three crashed ("The
  Newton-Raphson optimizer did not converge"), and two reached degenerate modes.
- **The instability reaches chap.** One of the four monthly chap repeats produced no
  evaluation: INLA crashed with the same Newton-Raphson error in one backtest split
  (`results/chap_repeats/service_container.log`).
- **Two candidate causes remain untested:**
  - randomness inside INLA's optimiser or its rescue paths;
  - the amd64 emulation on Apple Silicon. No native amd64 host was available.

## The L5 spread

CRPS of the R original through chap, repeated with nothing changed
(`results/chap_repeats.tsv`):

| Dataset | Runs | CRPS min | CRPS max |
|---|---|---|---|
| weekly (Nicaragua) | 4 | 21.92 | 22.10 |
| monthly (EWARS example) | 3 of 4 (one crashed) | 1123.9 | 1138.0 |

Batch 2's run1 (1129.1 monthly, 22.10 weekly) falls inside both ranges
(`../01_referenceThroughChap/results/run1/reference_scores.tsv`).

## Ledgers

JC-14 to JC-19 and CH-20 to CH-22 were added. CH-21 records that the host slept during the
run, so wall-clock times are upper bounds. `run.sh` now keeps the host awake. The rendered
documents are in `AI-generated/translation-record/`.

## For the human

**Batch 5 is on hold for your decision** (plan §3: when an anchor does not behave as
assumed, stop and report). The plan's yardstick is the R reference's own variability. That
variability turns out to have two parts:

- a spread between healthy fits, large at L3 on monthly data;
- occasional degenerate fits and crashes, which INLA does not flag as failures.

How the tolerance file treats the second part decides what "similar" means. Three readings:

1. **The reference as it runs.** Degenerate fits and crashes are part of the R behaviour
   that Python is compared against. This is the most literal reading, but it makes the
   L3 yardstick very wide.
2. **Healthy R fits only.** Fits flagged by VB aborts, a collapsed number of integration
   points, or a crash are excluded from the noise floor, by a rule written before any Python
   result exists. The flags are already in `fit_summary.tsv`. The exclusion would be a
   logged judgment call. This is the recommended reading.
3. **Investigate the cause first.** For example, run the image on native amd64, or fit with
   INLA's own diagnostics on. This costs a batch, and may show the instability to be an
   artefact of emulation.

Also: Q1–Q3 in plan §4 still stand with their defaults.

## Next

Batch 5, the fidelity metrics and the tolerance file, once the reading above is chosen.
