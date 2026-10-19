# Claim

How far is the posterior of the same model, sampled by full MCMC (NUTS) rather than approximated, from INLA's (L3) and from INLA's predictive distribution (L4), and therefore how much of the agreement between the Python model and the R reference rests on INLA's approximation?

## Children

kind: -
main-path: -

## Environment

inherits: the project main environment (`environment/`)

## Answers

1. **The sampled density is the one candidate (a) approximates.** At 20 random points per
   dataset x variant x parametrisation, the NumPyro log density and the joint density written
   with the package's own pieces differ by a constant, to at most 4.4e-9 log units
   (`results/target_check.tsv`). Differences between (b) and (a) are therefore the
   approximation, not the model.
2. **The chains converged.** Over 24 runs of 4 chains x 1000 kept draws: max R-hat 1.032,
   min ESS 179, 1 divergence, 87 tree-depth hits spread over 5 runs
   (`results/summary_cost.tsv`, `results/mcmc_fits/mcmc_fits_summary.tsv`). This needed the
   "split" parametrisation of intercept and iid effect (JC-33, CH-28).
3. **Latent field (L3): no difference beyond the MCMC's own noise.** For fixed and random
   effects, the median shift of the posterior mean is 0.002-0.031 posterior sd against clean
   R fits and 0.002-0.026 against (a), while independent MCMC runs differ from each other by
   0.003-0.039 (`results/summary_l3.tsv`).
4. **Hyperparameters (L3): small, systematic, lower precisions under MCMC.** Shifts against
   (a) are 0.027-0.066 sd (median per group), against clean R fits 0.009-0.048, against other
   MCMC runs 0.006-0.027 (`results/summary_l3.tsv`). The MCMC mean is below (a)'s for 24 of
   26 hyperparameters; the largest shift is the monthly seasonal precision, -0.16 sd against
   (a) and -0.09 against R on the default variant. Posterior sds agree to within 5 %
   (sd ratio 0.950-1.026 against (a)) (`results/summary_hyperparameters.tsv`).
5. **Predictive (L4): indistinguishable from the Monte Carlo floor.** On forecast rows, the
   median mean shift is 0.026-0.032 pooled sd against (a), 0.026-0.031 against R and
   0.027-0.034 between MCMC runs; W1 0.051-0.055 sd in all three; 90 % interval width ratio
   0.984-1.009 (`results/summary_l4.tsv`).
6. **So the agreement does not rest on INLA's approximation** in any way that reaches the
   forecasts: exact Bayes on the same model gives the same predictive distribution as INLA and
   as candidate (a). What INLA's approximation does change is visible only in the
   hyperparameters, by a few hundredths of a posterior sd.
7. **Cost**: 56-494 s per fit (one run at 1999 s, see `provenance/mcmc_fits.md`), against
   1-11 s for candidate (a) on the same inputs (`results/summary_cost.tsv`); 1.9 h for all 24.
