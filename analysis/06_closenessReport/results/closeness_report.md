# How close the Python EWARS model is to the R original

The Python model (`analysis/05_pythonModel/scripts/chapkit_ewars_python/`) is set beside the R original (`chapkit_ewars_model` @ 964eea8b, R-INLA 25.10.19) at five layers, on the two development datasets: monthly EWARS example (23 locations) and weekly Nicaragua (10 locations). At each layer the same measures are also given for the R original against itself, with nothing changed between runs, so that the reader can judge the Python–R distance against the R–R distance. Nothing is excluded: every R fit is labelled *clean*, *flagged* or *crashed* (04_fidelityMetrics), and pairs involving a flagged R fit are shown separately.

## The R original's own behaviour

Seeded refits on identical inputs (2 datasets × 4 config variants, 5 replicates plus one seeded repeat of the default), and single-threaded diagnostic fits:

| run_set | dataset | variant | clean | flagged | crashed |
|---|---|---|---|---|---|
| fits | monthly_ewars | default | 5 | 1 | 0 |
| fits | monthly_ewars | nlags_3_6 | 5 | 0 | 0 |
| fits | monthly_ewars | no_covariates | 5 | 0 | 0 |
| fits | monthly_ewars | region_seasonal | 5 | 0 | 0 |
| fits | weekly_nicaragua | default | 6 | 0 | 0 |
| fits | weekly_nicaragua | nlags_3_6 | 5 | 0 | 0 |
| fits | weekly_nicaragua | no_covariates | 5 | 0 | 0 |
| fits | weekly_nicaragua | region_seasonal | 5 | 0 | 0 |
| thread_diagnostic | monthly_ewars | default | 3 | 0 | 0 |
| thread_diagnostic | weekly_nicaragua | default | 0 | 2 | 1 |

*Source: `04_fidelityMetrics/results/r_fit_health_counts.tsv`. Flagged: a logged VB-correction abort, a non-zero mode status, or fewer than half the integration points.*

Evaluations of the R original through chap (batch 2's run plus the repeats):

| dataset | completed | crashed |
|---|---|---|
| monthly_ewars | 4 | 1 |
| weekly_nicaragua | 5 | 0 |

*Source: `04_fidelityMetrics/results/l5_evaluations.tsv`. A crashed evaluation produced no scores: INLA stopped in one backtest split.*

## L1–L2: model frame and cross-basis

| dataset | variant | frame_max_abs_diff | basis_max_abs_diff | string_mismatches | na_pattern_mismatches |
|---|---|---|---|---|---|
| monthly_ewars | default | 0.0e+00 | 4.4e-16 | 0 | 0 |
| monthly_ewars | nlags_3_6 | 0.0e+00 | 4.4e-16 | 0 | 0 |
| monthly_ewars | no_covariates | 0.0e+00 | 0.0e+00 | 0 | 0 |
| monthly_ewars | region_seasonal | 0.0e+00 | 4.4e-16 | 0 | 0 |
| weekly_nicaragua | default | 6.8e-21 | 3.3e-16 | 0 | 0 |
| weekly_nicaragua | nlags_3_6 | 6.8e-21 | 4.4e-16 | 0 | 0 |
| weekly_nicaragua | no_covariates | 6.8e-21 | 0.0e+00 | 0 | 0 |
| weekly_nicaragua | region_seasonal | 6.8e-21 | 3.3e-16 | 0 | 0 |

*Source: `05_pythonModel/01_dataLayer/results/l1_l2_comparison.tsv`. Python against the frame and cross-basis the R reference built from the same files. The R side is identical across all its refits (03_referenceHarness), so the R–R distance here is 0.*

## The model pieces and the fitted objective

| quantity | max difference from INLA / R |
|---|---|
| cyclic_rw1_scale | 1.3e-08 |
| nb_loglik | 5.9e-11 |
| pc_mgamma_log_density | 2.4e-12 |
| rw1_null_space | 0.0e+00 |
| sum_to_zero_basis_orthonormality | 2.2e-16 |
| sum_to_zero_basis_sums | 1.2e-15 |

*Source: `05_pythonModel/02_modelPrimitives/results/primitives_check.tsv` (scale factor: relative; the rest absolute).*

The Python Laplace log posterior of the hyperparameters, evaluated at INLA's own integration points of every R fit, against the relative log posterior INLA recorded there (log units):

| dataset | variant | max |difference|, clean R fits | max |difference|, flagged R fit |
|---|---|---|---|
| monthly_ewars | default | 0.0154 | 34338.2158 |
| monthly_ewars | nlags_3_6 | 0.0142 | – |
| monthly_ewars | no_covariates | 0.0209 | – |
| monthly_ewars | region_seasonal | 0.0186 | – |
| weekly_nicaragua | default | 0.0001 | – |
| weekly_nicaragua | nlags_3_6 | 0.0001 | – |
| weekly_nicaragua | no_covariates | 0.0001 | – |
| weekly_nicaragua | region_seasonal | 0.0001 | – |

*Source: `05_pythonModel/03_inference/a_laplaceCcd/results/objective_at_inla_configs.tsv`, with each R fit's health from `04_fidelityMetrics/results/r_fit_health.tsv`. At the flagged fit's points the two objectives disagree by thousands of log units: INLA's recorded values there come from a degenerate fit.*

## L3: posterior

Shift in posterior mean, in pooled posterior sds, per quantity; the cells give the range over pairs of the per-pair median |shift| (max |shift| in brackets). Groups: hyperparameters (NB size and precisions), fixed effects (intercept and cross-basis coefficients), random effects (all values of all terms).

| dataset | variant | quantities | R vs R, clean pairs | Python vs R, clean R | R vs R, a flagged fit | Python vs R, flagged R |
|---|---|---|---|---|---|---|
| monthly_ewars | default | hyperparameters | 0.009 – 0.594 (0.01 – 1.13) | 0.002 – 0.596 (0.06 – 0.89) | 13.6 – 20.1 | 20.0 – 20.1 |
| monthly_ewars | default | fixed effects | 0.001 – 0.009 (0.01 – 0.10) | 0.000 – 0.005 (0.00 – 0.09) | 2.3 – 2.3 | 2.3 |
| monthly_ewars | default | random effects | 0.001 – 0.057 (0.00 – 0.09) | 0.000 – 0.038 (0.00 – 0.06) | 4.3 – 22.3 | 4.3 – 22.2 |
| monthly_ewars | nlags_3_6 | hyperparameters | 0.007 – 0.055 (0.03 – 0.25) | 0.004 – 0.064 (0.01 – 0.19) | – | – |
| monthly_ewars | nlags_3_6 | fixed effects | 0.001 – 0.004 (0.01 – 0.02) | 0.000 – 0.003 (0.00 – 0.02) | – | – |
| monthly_ewars | nlags_3_6 | random effects | 0.001 – 0.025 (0.00 – 0.04) | 0.000 – 0.019 (0.00 – 0.03) | – | – |
| monthly_ewars | no_covariates | hyperparameters | 0.003 – 0.016 (0.02 – 0.34) | 0.002 – 0.020 (0.03 – 0.24) | – | – |
| monthly_ewars | no_covariates | fixed effects | 0.000 – 0.001 (0.00 – 0.00) | 0.000 – 0.001 (0.00 – 0.00) | – | – |
| monthly_ewars | no_covariates | random effects | 0.000 – 0.012 (0.00 – 0.02) | 0.000 – 0.010 (0.00 – 0.02) | – | – |
| monthly_ewars | region_seasonal | hyperparameters | 0.008 – 0.027 (0.07 – 0.32) | 0.004 – 0.024 (0.05 – 0.33) | – | – |
| monthly_ewars | region_seasonal | fixed effects | 0.001 – 0.004 (0.01 – 0.04) | 0.001 – 0.003 (0.01 – 0.03) | – | – |
| monthly_ewars | region_seasonal | random effects | 0.001 – 0.086 (0.01 – 0.14) | 0.001 – 0.063 (0.00 – 0.10) | – | – |
| weekly_nicaragua | default | hyperparameters | 0.000 – 0.018 (0.00 – 0.02) | 0.011 – 0.028 (0.02 – 0.05) | – | – |
| weekly_nicaragua | default | fixed effects | 0.000 – 0.001 (0.00 – 0.01) | 0.000 – 0.001 (0.00 – 0.01) | – | – |
| weekly_nicaragua | default | random effects | 0.000 – 0.004 (0.00 – 0.02) | 0.000 – 0.002 (0.00 – 0.01) | – | – |
| weekly_nicaragua | nlags_3_6 | hyperparameters | 0.002 – 0.148 (0.01 – 0.89) | 0.012 – 0.164 (0.02 – 0.89) | – | – |
| weekly_nicaragua | nlags_3_6 | fixed effects | 0.000 – 0.002 (0.00 – 0.01) | 0.000 – 0.001 (0.00 – 0.01) | – | – |
| weekly_nicaragua | nlags_3_6 | random effects | 0.000 – 0.017 (0.00 – 0.07) | 0.000 – 0.009 (0.00 – 0.04) | – | – |
| weekly_nicaragua | no_covariates | hyperparameters | 0.001 – 0.007 (0.00 – 0.01) | 0.017 – 0.025 (0.02 – 0.03) | – | – |
| weekly_nicaragua | no_covariates | fixed effects | 0.000 – 0.000 (0.00 – 0.00) | 0.000 – 0.000 (0.00 – 0.00) | – | – |
| weekly_nicaragua | no_covariates | random effects | 0.000 – 0.001 (0.00 – 0.01) | 0.000 – 0.001 (0.00 – 0.00) | – | – |
| weekly_nicaragua | region_seasonal | hyperparameters | 0.003 – 0.025 (0.01 – 0.05) | 0.005 – 0.018 (0.02 – 0.05) | – | – |
| weekly_nicaragua | region_seasonal | fixed effects | 0.000 – 0.003 (0.00 – 0.02) | 0.000 – 0.002 (0.00 – 0.01) | – | – |
| weekly_nicaragua | region_seasonal | random effects | 0.001 – 0.015 (0.00 – 0.05) | 0.000 – 0.010 (0.00 – 0.03) | – | – |

*Sources: `04_fidelityMetrics/results/l3_r_vs_r_pairs.tsv`, `05_pythonModel/03_inference/a_laplaceCcd/results/l3_python_vs_r_pairs.tsv`. Python: 3 runs per variant (the fit is deterministic; runs differ by sampler seed), each against each R run.*

Where the hyperparameter mode lands (INLA's internal scale):

| dataset | variant | theta | R clean fits (range) | Python | R flagged fits |
|---|---|---|---|---|---|
| monthly_ewars | default | log size | 0.649 – 0.664 | 0.650 | 0.29 |
| monthly_ewars | default | log prec iid | -0.501 – -0.448 | -0.455 | 5.67 |
| monthly_ewars | default | log prec RW1 | 1.766 – 2.039 | 1.775 | 3.64 |
| monthly_ewars | nlags_3_6 | log size | 0.645 – 0.650 | 0.649 | – |
| monthly_ewars | nlags_3_6 | log prec iid | -0.382 – -0.360 | -0.378 | – |
| monthly_ewars | nlags_3_6 | log prec RW1 | 1.515 – 1.897 | 1.807 | – |
| monthly_ewars | no_covariates | log size | 0.595 – 0.597 | 0.595 | – |
| monthly_ewars | no_covariates | log prec iid | -0.598 – -0.587 | -0.591 | – |
| monthly_ewars | no_covariates | log prec RW1 | 1.425 – 1.703 | 1.641 | – |
| monthly_ewars | region_seasonal | log size | 1.069 – 1.071 | 1.071 | – |
| monthly_ewars | region_seasonal | log prec iid | -0.356 – -0.346 | -0.350 | – |
| monthly_ewars | region_seasonal | log prec RW1 | 1.965 – 2.326 | 2.115 | – |
| monthly_ewars | region_seasonal | log prec RW1 by location | 2.145 – 2.168 | 2.163 | – |
| weekly_nicaragua | default | log size | 0.681 – 0.681 | 0.681 | – |
| weekly_nicaragua | default | log prec iid | -0.323 – -0.306 | -0.322 | – |
| weekly_nicaragua | default | log prec RW1 | 2.754 – 2.784 | 2.771 | – |
| weekly_nicaragua | nlags_3_6 | log size | 0.682 – 0.684 | 0.683 | – |
| weekly_nicaragua | nlags_3_6 | log prec iid | -0.343 – -0.287 | -0.338 | – |
| weekly_nicaragua | nlags_3_6 | log prec RW1 | 2.650 – 2.855 | 2.799 | – |
| weekly_nicaragua | no_covariates | log size | 0.654 – 0.654 | 0.654 | – |
| weekly_nicaragua | no_covariates | log prec iid | -0.313 – -0.308 | -0.312 | – |
| weekly_nicaragua | no_covariates | log prec RW1 | 2.535 – 2.548 | 2.544 | – |
| weekly_nicaragua | region_seasonal | log size | 0.732 – 0.734 | 0.733 | – |
| weekly_nicaragua | region_seasonal | log prec iid | -0.351 – -0.331 | -0.337 | – |
| weekly_nicaragua | region_seasonal | log prec RW1 | 2.780 – 2.860 | 2.809 | – |
| weekly_nicaragua | region_seasonal | log prec RW1 by location | 3.474 – 3.516 | 3.507 | – |

*Sources: `04_fidelityMetrics/results/r_fit_health.tsv`; `05_pythonModel/03_inference/a_laplaceCcd/results/python_fits/fits/*/*/rep1/fit_info.json`.*

## L4: predictive samples (forecast rows)

Per forecast row, from the 1000 samples: the shift in predictive mean in pooled predictive sds, and the Wasserstein-1 distance between the two sample sets in pooled sds; cells give the median over pairs of the per-pair median. With 1000 samples, Monte Carlo error alone gives about 0.03 and 0.05; the Python–Python column (sampler seed only) shows that floor directly. The 90 % interval-width ratio is the median over pairs of the per-pair median.

| dataset | variant | R vs R, clean | Python vs R, clean R | Python vs Python | pairs with a flagged R fit |
|---|---|---|---|---|---|
| monthly_ewars | default | 0.030 / 0.054 / 1.00 | 0.032 / 0.053 / 1.00 | 0.028 / 0.051 / 0.99 | 0.941 / 0.941 / 0.38 |
| monthly_ewars | nlags_3_6 | 0.026 / 0.051 / 1.00 | 0.031 / 0.052 / 1.00 | 0.031 / 0.055 / 1.00 | – |
| monthly_ewars | no_covariates | 0.028 / 0.053 / 1.00 | 0.030 / 0.052 / 1.00 | 0.028 / 0.050 / 1.02 | – |
| monthly_ewars | region_seasonal | 0.031 / 0.055 / 1.00 | 0.030 / 0.053 / 1.00 | 0.026 / 0.050 / 1.00 | – |
| weekly_nicaragua | default | 0.027 / 0.052 / 1.00 | 0.028 / 0.052 / 1.00 | 0.032 / 0.052 / 1.00 | – |
| weekly_nicaragua | nlags_3_6 | 0.031 / 0.050 / 1.00 | 0.027 / 0.050 / 1.00 | 0.027 / 0.050 / 1.00 | – |
| weekly_nicaragua | no_covariates | 0.034 / 0.057 / 1.01 | 0.028 / 0.050 / 1.00 | 0.023 / 0.049 / 1.00 | – |
| weekly_nicaragua | region_seasonal | 0.029 / 0.051 / 1.00 | 0.036 / 0.055 / 1.00 | 0.034 / 0.056 / 1.00 | – |

*Cells: mean shift / W1 / width ratio. Sources: `04_fidelityMetrics/results/l4_r_vs_r_pairs.tsv`, `05_pythonModel/03_inference/a_laplaceCcd/results/l4_python_vs_r_pairs.tsv`.*

## L5: chap's backtest scores

Aggregate CRPS (lower is better), each run of each model, and chap's baselines:

| dataset | R original (CRPS per run) | Python (CRPS per run) | seasonal_median | persistence | global_median |
|---|---|---|---|---|---|
| monthly_ewars | 1123.88, 1127.98, 1129.11, 1138.04; 1 crashed | 1115.66, 1125.78, 1132.08 | 740.72 | 822.53 | 1129.66 |
| weekly_nicaragua | 21.92, 21.97, 21.98, 22.10, 22.10 | 21.95, 21.96, 22.16 | 31.65 | 11.21 | 30.54 |

Paired per-row differences in CRPS (each row a location × forecast period × horizon), median over pairs of runs:

| dataset | comparison | mean_diff | median_abs_diff | mean_abs_diff |
|---|---|---|---|---|
| monthly_ewars | python_vs_python | -10.126 | 6.361 | 44.066 |
| monthly_ewars | python_vs_r | -4.643 | 7.004 | 51.842 |
| monthly_ewars | r_vs_r | 4.666 | 8.613 | 67.330 |
| weekly_nicaragua | python_vs_python | 0.199 | 0.504 | 0.998 |
| weekly_nicaragua | python_vs_r | -0.015 | 0.532 | 0.991 |
| weekly_nicaragua | r_vs_r | 0.116 | 0.529 | 0.995 |
| monthly_ewars | python_vs_global_median | 3.876 | 169.150 | 1020.657 |
| monthly_ewars | python_vs_persistence | -303.258 | 137.375 | 845.407 |
| monthly_ewars | python_vs_seasonal_median | -385.061 | 113.188 | 942.149 |
| weekly_nicaragua | python_vs_global_median | 8.580 | 8.592 | 18.048 |
| weekly_nicaragua | python_vs_persistence | -10.746 | 7.996 | 13.525 |
| weekly_nicaragua | python_vs_seasonal_median | 9.696 | 10.049 | 18.205 |

*mean_diff: second minus first, so negative favours the second. Sources: `05_pythonModel/04_throughChap/results/l5_evaluations.tsv`, `l5_pairs.tsv`; the R evaluations from `04_fidelityMetrics/results/l5_rows/`.*

## Reading this report

No threshold is applied. For each layer, compare the *Python vs R, clean R* column with the *R vs R, clean* column, and the flagged columns with each other, to judge whether the Python model is as close to the R original as the R original is to itself. The L5 baselines put the size of any Python–R gap in proportion.
