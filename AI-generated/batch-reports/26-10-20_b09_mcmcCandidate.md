# Batch 9 — inference candidate (b): exact Bayes by MCMC

Generated from [[26-10-14_pythonEwarsForChap]] — batch 9 (phase C).

**The question.** The Python model agrees with the R reference. Candidate (a) reproduces
INLA's approximation step by step, so that agreement could rest on sharing INLA's
approximation rather than on getting the posterior right. Candidate (b) fits the same model by
full MCMC, which approximates nothing beyond Monte Carlo error. Where (b) differs from INLA,
the difference is INLA's approximation.

The node is `analysis/05_pythonModel/03_inference/b_mcmcNuts/`. Its answers are in its
`claim.md`, and the main-path decision is in `03_inference/claim.md`.

## What was built

- **The sampler.** NumPyro's NUTS samples the joint posterior of the hyperparameters and
  the latent field (`scripts/mcmc_nuts.py`). It runs 4 chains of 1000 warm-up and 1000 kept
  iterations, 3 independent runs per dataset × variant, all on the R harness's inputs.
- **The same density as (a).** The sampled density is the one candidate (a) approximates,
  including INLA's convention for the latent prior's normalising constant. The check is that
  the two densities differ by a constant, to at most 4.4e-9 log units, on every dataset and
  variant (`results/target_check.tsv`).
- **A reparametrisation.** The likelihood sees the intercept and the iid region–year
  effect only through their sum. Sampled as they are, they form a ridge that took the
  sampler up to 15 minutes for 450 iterations on the weekly data, without converging. It
  samples instead the level the data see, the deviations of the iid effect, and the iid
  mean, which is set by its prior alone. The model is the same, and so is the density. This
  made the weekly no-covariates test 40 times faster (CH-28, JC-33).
- **Converged.** Over the 24 runs, the maximum R-hat is 1.032, the minimum ESS is 179, and
  there is 1 divergence.

## What it shows

| | (b) vs clean R fits | (b) vs (a) | (b) vs (b) |
|---|---|---|---|
| L3 latent field, median shift (posterior sd) | 0.002–0.031 | 0.002–0.026 | 0.003–0.039 |
| L3 hyperparameters, median shift (posterior sd) | 0.009–0.048 | 0.027–0.066 | 0.006–0.027 |
| L4 forecast rows, median mean shift (pooled sd) | 0.026–0.031 | 0.026–0.032 | 0.027–0.034 |
| L4 forecast rows, median W1 (pooled sd) | 0.051–0.055 | 0.051–0.053 | 0.050–0.055 |

Ranges are over datasets, variants and parameter groups (`results/summary_l3.tsv`,
`summary_l4.tsv`).

- **Forecasts.** The predictive distribution is the same under exact Bayes, under INLA
  and under candidate (a), to the Monte Carlo floor of 1000 samples.
- **Latent field.** Fixed and random effects agree to within the MCMC's own run-to-run
  noise.
- **Hyperparameters.** This is the one place INLA's approximation shows. MCMC gives
  slightly lower precisions, for 24 of 26 hyperparameters against (a). The shift is a few
  hundredths of a posterior sd, at most 0.16 sd, for the monthly seasonal precision
  (`results/summary_hyperparameters.tsv`). Posterior sds agree to within 5 %.
- **Cost.** A (b) fit takes 1–8 minutes, against 1–11 s for (a).

## Decision

**Candidate (a) stays the main path** (JC-34):

- its forecasts are the same as (b)'s and the R reference's;
- it is the closer of the two to INLA on the hyperparameters;
- it is 10–100 times cheaper, which counts inside a chap backtest.

(b) stays in the tree, runnable. It was not run through chap (L5), because L3–L4 already
settle the choice.

## Ledgers

JC-32 to JC-34 and CH-28 were added; the translation record is re-rendered. NumPyro 0.22.0
and JAX 0.11.2 were added to the main environment, with every earlier pin unchanged. The
service image does not include them.

## For the human

1. **Your question is answered: the differences are small.** Exact Bayes does not give
   forecasts different from INLA's on this model. The agreement between the Python model and
   R does not depend on copying INLA's approximation.
2. One fit ran at 1999 s, against 300–380 s for the other two runs of the same variant, with
   no difference in the sampler's own diagnostics. It is most likely the host sleeping, as in
   CH-21. It is recorded and does not affect any result.
3. Still open: phase D (stability), whose budget is to be set, and phase E (the holdout).

## Next

Phase D, the stability run: a perturbation manifest from the JC ledger, costed against the
measured run times, and a compute budget to set with you.
