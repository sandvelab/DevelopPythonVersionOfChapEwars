# Claim

How does the R original CHAP-EWARS model, run as its pinned chapkit image, score under chap-core's own backtest evaluation on the development data, set beside chap-core's built-in baselines through the same pipeline — and exactly what commands, from a fresh shell, produce those scores?

## Children

kind: -
main-path: -

## Environment

override: `env/` — this node runs no project analysis code; it drives chap-core, so its
environment is chap-core at the pinned commit from its own lockfile, plus the EWARS image
pinned by digest (`env/README.md`, JC-03, JC-08).

## Answers

1. **The R original runs through chap-core's `chap eval` as a chapkit service, on both
   development datasets, once each file is reduced to the six-column data contract.** The
   monthly example file as shipped makes INLA fail in every backtest. chap's
   `climatology` weather provider forecasts the file's pre-derived `month` column for the
   forecast window as non-integers, and `predict.R` uses that column as it is
   (`results/diagnose_monthly/`, CH-07, JC-05).
2. **The R reference's first chap scores** (CRPS, 7 splits × 3 periods, climatology
   weather): monthly 1129.1, weekly 22.10 (`results/run1/reference_scores.tsv`).
   - On monthly data EWARS is beaten by the seasonal_median (740.7) and persistence (822.5)
     baselines and level with global_median (1129.7).
   - On weekly data it beats both medians (30.5, 31.7) and is beaten by persistence (11.2).
3. **The R reference's chap scores are not reproducible run to run**, because nothing seeds
   it (CH-10). Two independent monthly runs gave CRPS 1129.1 and 1125.7
   (`results/tutorial_check/verdict.txt`).
4. **The tutorial's commands are complete.** Run verbatim in an empty shell, they reproduce
   run1's input byte for byte and its seasonal_median scores exactly
   (`results/tutorial_check/verdict.txt`: PASS).
