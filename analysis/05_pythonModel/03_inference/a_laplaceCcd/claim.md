# Claim

How close to INLA does an INLA-style approximation written in Python come: a Gaussian approximation of the latent field at each hyperparameter value, the hyperparameter mode and a central composite design over it, and predictive draws from the resulting mixture?

## Children

kind: -
main-path: -

## Environment

inherits: the project main environment (`environment/`)

## Answers

1. **The objective matches INLA's.** At INLA's own integration points, the Python Laplace log
   posterior of the hyperparameters equals INLA's relative log posterior to at most 2e-4 log
   units on the weekly data and 0.021 on the monthly, for every clean R fit
   (`results/objective_at_inla_configs.tsv`).
2. **L3: inside the R reference's own spread** (`results/l3_python_vs_r_pairs.tsv`): against
   clean R fits, posterior means shift by a median of at most 0.025 posterior sd for the
   hyperparameters and at most 0.024 sd for fixed and random effects, on every dataset and
   variant; the corresponding R-vs-R figures are given in 04_fidelityMetrics answer 3.
3. **L4: at the Monte Carlo floor** (`results/l4_python_vs_r_pairs.tsv`, forecast rows): median
   mean shift 0.027-0.036 pooled sd, W1 0.050-0.055 sd, width ratio 0.999-1.004 against clean R
   fits; Python against Python (sampler seed only) gives 0.023-0.034 and 0.049-0.056.
4. **Cost**: a fit takes 1-11 s natively (`results/python_fits/python_fits_timings.tsv`), against
   7-307 s of INLA fit time under amd64 emulation, an upper bound because the host slept during
   that run (03_referenceHarness, fit_summary.tsv; CH-21).
5. The Python fit is deterministic. Unlike INLA's refits (CH-20) it cannot land in a different
   mode on identical inputs, and none of its 24 fits had a VB abort or a dropped integration
   point (`results/python_fits/fits/*/*/rep*/fit_info.json`).
