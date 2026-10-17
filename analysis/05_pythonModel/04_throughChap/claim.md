# Claim

Does the Python model run through chap-core's backtest exactly as the R original does, and how do its chap scores compare with the R original's and with chap's baselines?

## Children

kind: -
main-path: -

## Environment

inherits: the project main environment (`environment/`) for `compare_l5.py`;
override: `run_python_through_chap.sh` drives chap-core at its pinned commit (installed by
`../../04_fidelityMetrics/scripts/ensure_chap_core.sh`) against the Python service's Docker
image, built from `../scripts/chapkit_ewars_python/` at the run's commit (`results/chap_runs/image_id.txt`);
`nc_to_rows.py` runs under chap-core's environment, as in 04_fidelityMetrics.

## Answers

1. **chap-core drives the Python service exactly as it drives the R original**: the same chap
   commit, inputs, config file and backtest settings; 6 of 6 evaluations completed
   (`results/chap_runs/timings.tsv`), 4.8-6.0 min monthly and about 2 min weekly.
2. **Its scores overlap the R original's run-to-run range** (`results/l5_evaluations.tsv`):
   monthly CRPS 1115.7, 1125.8, 1132.1 against the R original's 1123.9-1138.0 (4 completed, 1
   crashed), one Python run 8.2 below the lowest R run; weekly 21.95, 21.96, 22.16 against
   21.92-22.10, one Python run 0.06 above the highest. Across its 3 sampler seeds the Python
   model spans 16.4 (monthly) and 0.21 (weekly), against 14.2 and 0.18 across the R runs. Paired per row, Python-vs-R CRPS
   differences have a median |difference| of 7.0 (monthly) and 0.53 (weekly) against 8.6 and
   0.53 between R runs (`results/l5_pairs.tsv`).
3. **Against chap's baselines, it ranks as the R original does**: worse than seasonal_median
   (740.7) and persistence (822.5) on the monthly data and level with global_median (1129.7);
   on the weekly data better than global_median (30.5) and seasonal_median (31.7), worse than
   persistence (11.2).
4. **The run guide works as written** from a fresh shell (`results/guide_check/`, exit code 0),
   and its evaluation reproduces run1's CRPS to the last digit (21.9456264): the same inputs give
   the same scores.
