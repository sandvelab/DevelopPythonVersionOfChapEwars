# Claim

How should the closeness of two runs of the EWARS model be described at each fidelity layer (L1 frame, L2 cross-basis, L3 posterior, L4 predictive, L5 chap scores), and what does that description show when both runs are the R reference itself, its degenerate fits and crashes counted rather than excluded?

## Children

kind: -
main-path: -

## Environment

inherits: the project main environment (`environment/`) for `fidelity.py` and
`describe_r_reference.py`;
override: `nc_to_rows.py` runs under chap-core's own environment (pinned commit `b8c8f788`,
installed from its lockfile into `work/` by `scripts/ensure_chap_core.sh`), because reading
chap's netCDF evaluation files needs xarray and a netCDF backend, which the main environment
does not carry.

## Answers

1. **Closeness is described, not judged** (plan §4b, 2026-10-17; JC-25). L3: per posterior
   quantity, the shift in mean in pooled posterior sds and the sd ratio. L4: per forecast row,
   the shift in predictive mean and the Wasserstein-1 distance in pooled predictive sds, and the
   90 % interval-width ratio. L5: aggregate CRPS and paired per-row CRPS differences. The per-row
   sample CRPS reproduces chap's aggregate exactly (`results/l5_rows/`, weekly rep1 21.9186).
2. **R fits as they run** (`results/r_fit_health_counts.tsv`): 41 of 42 sweep fits clean, 1
   flagged (monthly default, the seeded repeat); single-threaded diagnostics: monthly 3 clean,
   weekly 2 flagged and 1 crashed. Through chap: 1 of 5 monthly evaluations crashed, 0 of 5 weekly
   (`results/l5_evaluations.tsv`).
3. **Between clean R refits** (`results/l3_r_vs_r_pairs.tsv`): latent quantities (fixed and
   random effects) shift by a median of at most 0.04 posterior sd per pair; hyperparameters by
   up to 0.59 sd in median and 1.13 sd at most (monthly default, the RW1 precision).
   **Pairs with the flagged fit**: hyperparameters 20 sd in median, up to 1060 sd.
4. **At L4, clean R refits differ at the Monte Carlo floor** (`results/l4_r_vs_r_pairs.tsv`,
   forecast rows): median mean shift 0.026-0.034 pooled sd, W1 0.050-0.057 sd, width ratio
   0.997-1.006, on every dataset and variant. The flagged fit: mean shift 0.94 sd, width ratio
   0.38.
5. **At L5, R runs differ by** (`results/l5_r_vs_r_pairs.tsv`, `l5_evaluations.tsv`): monthly
   CRPS 1123.9-1138.0 over 4 completed runs, per-row median |difference| 6.5-10.9; weekly
   21.92-22.10 over 5 runs, per-row median |difference| 0.41-0.56. chap's baselines on the same
   backtest: monthly seasonal_median 740.7, persistence 822.5, global_median 1129.7; weekly
   persistence 11.2, global_median 30.5, seasonal_median 31.7.
