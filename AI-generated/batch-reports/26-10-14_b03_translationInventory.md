# Batch 3 — Translation inventory

Generated from [[26-10-14_pythonEwarsForChap]] — batch 3 (phase B).

Node: `analysis/02_translationInventory/`. The inventory itself is
`analysis/02_translationInventory/results/translation_inventory.md`.

## What was done

- **The R sources were archived at the versions the reference runs.**
  `AI-internal/data-acquisition/fetch_r_sources.sh` first read the versions inside the
  reference image: INLA 25.10.19, dlnm 2.4.10, R 4.5.0. It then archived into
  `Archive/r-sources/`:
  - **r-inla** at tag `Version_25.10.19` (commit `acb55f37`): the R code, the C program,
    GMRFLib's random-walk code, and the `.tex` documentation of latent models, likelihoods
    and priors;
  - **dlnm 2.4.10** from CRAN;
  - **from the image itself**: INLA's model definitions and control defaults, and the
    installed code of the functions the model uses.

  The image ships no INLA documentation (`inla.doc()` fetches it online), so the defaults
  were read from the installed package.
- **Every R call was listed by R's own parser**, inside the image, and resolved to the
  package that supplies it at runtime. The f() terms in the formula strings were extracted
  separately, since the parser sees them only as text. The result is 171 call sites and 65
  distinct calls (`results/r_calls.tsv`).
- **Each call was mapped to Python** (`scripts/call_mapping.tsv`, authored). A script joins
  the two and fails if any call is unmapped; none is.

  | Status | Distinct calls | Examples |
  |---|---|---|
  | gap: inference engine | 2 | `inla`, `inla.posterior.sample` |
  | gap: parallel port | 3 | iid with replicate; the two scaled cyclic RW1 terms |
  | counterpart, verify against R first | 3 | `crossbasis`, `equalknots` (dlnmpy); `rnbinom` |
  | own code, ported line by line | 13 | `offset_years_and_weeks`, `predict_chap`, ... |
  | direct equivalent | 36 | `rbind`, `substr`, `read.csv`, `mutate`, ... |
  | not needed in the service | 8 | `library`, `saveRDS`, `cat`, ... |

  (`results/coverage.tsv`)
- **The search for an existing Python INLA was archived.**
  `Archive/python-inla-candidates/` holds what it found and the basis for the verdict
  below.
- **The main environment was pinned**: Python 3.13.0, numpy, scipy, pandas, pyyaml, and
  dlnmpy at its pinned commit. A clean rebuild from `environment/lock.txt` matched it
  exactly.

## What the inventory shows

- **The installed INLA's defaults are part of the model** (`results/inla_defaults.tsv`).
  - **Size prior.** The negative-binomial size has a penalised-complexity prior,
    `pc.mgamma` with λ = 7 on log size. It is not a log-gamma prior, and this INLA version
    has no documentation page for it. The C source (`inla-priors.c`) is the specification
    the port follows (CH-14).
  - **Precision priors.** Both random-effect precisions have `loggamma(1, 5e-05)` priors.
    RW1 carries a sum-to-zero constraint by default.
  - **Engine settings.** The fit runs in `compact` mode, integrates over the hyperparameters
    with `int.strategy` `auto`, and applies a variational-Bayes correction to the means by
    default.
- **The predictive samples are more than Gaussian draws** (CH-15). By default, INLA's
  sampler:
  - picks a hyperparameter configuration with probability proportional to its posterior
    density, without the integration weights;
  - draws the latent field around the corrected means, under the constraints;
  - applies a skewness correction.
- **Three facts settle how `predict.R`'s sampling line is read.**
  - `theta[1]` is the size on its natural scale.
  - `Predictor` includes the `log(E)` offset, so `exp(Predictor)` is the mean. This is from
    the source; batch 4 confirms it numerically (CH-19).
  - INLA's negative binomial has mean μ and variance μ(1 + μ/size), the same parametrisation
    as R's `rnbinom(size, mu)` and scipy's `nbinom(n = size, p = size/(size + μ))`.
- **INLA sets missing covariate values to 0** (CH-16). The cross-basis is undefined for the
  first `nlag` rows of each location, and those rows enter the R fit as zeros. The Python
  data layer must do the same.
- **Unused packages.** `sf`, `spdep` and `jsonlite` are loaded but never called (CH-05,
  resolved in CH-17).
- **The port reproduces the R code's quirks rather than correcting them** (JC-11). These
  are:
  - the year shift computed from the last observed row of the whole frame;
  - ISO week 53 folded into the 52-week cycle;
  - historic rows with missing cases predicted alongside the future;
  - missing basis values treated as 0.

  A corrected variant would be a different model, so it belongs in the stability phase,
  not the main path.

## Inference candidate (c)

There is no existing Python INLA that this project can use as candidate (c) (JC-10).

- **pyINLA** is rejected on three counts:
  - it wraps the same compiled `inla` program R-INLA calls, so like rpy2 it calls INLA rather
    than reimplementing it;
  - its declared licence is "Proprietary", which conflicts with a public release;
  - it has no Python 3.13 build.
- **pylgm** (MIT, written from scratch, 878 tests) has much of what is needed:
  - a negative binomial with INLA's parametrisation;
  - offsets, iid effects, and RW1 with sum-to-zero and variance scaling;
  - a Laplace fit.

  It lacks cyclic RW1, `replicate`, and both of INLA's default priors used here. Extending it
  amounts to writing candidate (a). It is recorded as a possible building block for (a), to
  decide in batch 8.

Batches 8–10 therefore build candidates (a) and (b).

## Ledgers

JC-09 to JC-13 and CH-14 to CH-19 were added. CH-17 and CH-18 record the resolutions of
CH-05 and CH-13. The rendered documents are `AI-generated/translation-record/`.

## For the human

1. **JC-13 frames the whole L3 comparison.** Every candidate reproduces the model exactly:
   likelihood, INLA's default priors, constraints, and missing values as 0. How the
   posterior is approximated is free per candidate. A difference between Python and R at
   L3 can then be attributed to the inference engine.
2. **Candidate (c) is dropped** (JC-10). If you know of a Python INLA the search missed,
   it can still be assessed before batch 8.
3. Q1–Q3 in plan §4 still stand with their defaults.

## Next

Batch 4: the R reference harness. It must record, from each instrumented fit:
- the integration strategy `auto` resolved to, and the number of configurations;
- whether `exp(Predictor)` equals the mean (CH-19);
- the thread setting.

It must also seed both R's random-number generator and INLA's own `seed` argument. When
`seed` is non-zero, INLA forces single-threaded sampling.
