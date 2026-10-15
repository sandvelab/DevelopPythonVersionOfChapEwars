# Claim

What does the R reference produce at each fidelity layer (L1 derived frame, L2 cross-basis, L3 INLA posterior, L4 predictive samples) for each development dataset and config variant, and how much does it vary with nothing changed but the seed: across seeded refits at L3–L4, and across repeated chap evaluations at L5?

## Children

kind: -
main-path: -

## Environment

inherits: the project main environment (`environment/`) for the Python scripts;
override: `env/` — `instrument_reference.R` runs inside the R reference image, because the
harness must record what the reference itself computes; `run_chap_repeats.sh` drives
chap-core at its pinned commit, as node 01 does (`env/README.md`).

## Storage

`results/` holds 168 MB. Replicate 1 is kept in full. Replicates 2–5 and the seeded repeat
keep their summaries and predictions but not their per-row files: frames, linear
predictors, fitted values, posterior draws and offset checks. Those files are gitignored and
listed with sha256 in `results/fits_manifest.sha256` (JC-18). Because of answer 3, a re-run
does not regenerate them bit for bit.

## Answers

1. **L1 and L2 are deterministic.** The model frame, the cross-basis and its attributes,
   and the formula are identical across every refit of each dataset × variant
   (`results/refit_agreement.tsv`: model_frame max difference 0 for all 8;
   `results/seeded_repeat.tsv`). They are the fixed target for the Python data layer.
2. **INLA's `Predictor` includes the log(E) offset.** Rebuilding the linear predictor from
   one posterior draw's components leaves exactly log(E), to at most 1.2e-14, in all 47
   completed fits (`results/fit_summary.tsv`, CH-22). This confirms:
   - the replicate indexing of both replicated terms;
   - missing basis values entering as 0.
3. **The INLA fit is not reproducible on identical inputs (CH-20).**
   - **Refits differ.** Across 5 seeded refits, the posterior mode of the cyclic-RW1 log
     precision ranges over 1.77–2.04 (monthly, default) and 2.65–2.85 (weekly, nlags_3_6).
     Monthly fitted values differ by up to 472 cases (`results/fit_summary.tsv`,
     `results/refit_agreement.tsv`).
   - **One of 42 sweep fits was degenerate.** It reached NB size 1.34 and iid precision 290,
     with 4 integration points instead of 15, yet INLA reported success
     (`results/seeded_repeat.tsv`).
   - **Single-threaded fits also differ, so threading is not the cause.** On weekly data, one
     of the three crashed and two were degenerate (`results/thread_diagnostic.tsv`).
4. **The L4 draws are seeded, but cannot reproduce while the fit does not.** Every
   replicate's draws differ, as they must under different seeds
   (`results/refit_agreement.tsv`). The seeded repeat could not isolate the sampler's
   reproducibility, because its fit differed (answer 3).
5. **The L5 spread, from repeated unseeded chap evaluations of the R original**
   (`results/chap_repeats.tsv`):
   - weekly: CRPS 21.92–22.10 over 4 runs;
   - monthly: CRPS 1123.9–1138.0 over 3 runs.

   A fourth monthly run produced no evaluation: INLA crashed in one backtest split
   (`results/chap_repeats/service_container.log`, CH-20).
6. **What INLA resolved.**
   - `int.strategy auto` became a central composite design: 15 points with 3
     hyperparameters, 25 with 4 (14 and 24 in one fit each).
   - The fits ran in `compact` mode with 8:1 threads.
   - The median INLA fit time under emulation was 11–86 s by variant
     (`results/fit_summary.tsv`).
   - Wall-clock times include host sleep (CH-21).
