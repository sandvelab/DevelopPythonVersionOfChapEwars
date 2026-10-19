# Claim

Which Python inference strategy best reproduces INLA's posterior (L3) and predictive distribution (L4) for this model, fitted to the same design matrix?

## Children

kind: alternatives
main-path: a_laplaceCcd

## Environment

inherits: the project main environment (`environment/`)

## Answers

1. **Main path: `a_laplaceCcd`** (JC-34). Both candidates built, (a) the INLA-style
   approximation and (b) NUTS on the same density, give the same predictive distribution
   as each other and as the R reference, to the Monte Carlo floor of 1000 samples
   (a_laplaceCcd answer 3; b_mcmcNuts answer 5). On fidelity to INLA's posterior, (a) is
   the closer: its hyperparameter shifts against R are at most 0.025 sd (median), (b)'s
   0.009-0.048, which is INLA's own approximation showing in (b). On cost (a) takes 1-11 s per
   fit, (b) 1-8 minutes. Candidate (c) does not exist in usable form (JC-10).
2. What the comparison shows about INLA: its approximation is not what makes the Python model
   agree with the R reference. Exact Bayes differs from INLA only in the hyperparameters,
   by a few hundredths of a posterior sd, and not at all in the forecasts (b_mcmcNuts
   answers 4-6).
