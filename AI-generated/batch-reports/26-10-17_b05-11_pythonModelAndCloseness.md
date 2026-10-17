# Batches 5–8 (candidate a) and 11 — the Python model and how close it is

Generated from [[26-10-14_pythonEwarsForChap]] — batches 5, 6, 7, 8 (candidate a) and 11
(phases B–C), run in that order per plan §4b, 2026-10-17.

**The closeness report is `analysis/06_closenessReport/results/closeness_report.md`.** The
runnable model is `analysis/05_pythonModel/scripts/chapkit_ewars_python/`, and its `README.md`
is the guide to running it.

## What was built

| Node | What it holds |
|---|---|
| `04_fidelityMetrics` | The comparison measures (`scripts/fidelity.py`), and the R reference described against itself, every fit kept |
| `05_pythonModel/scripts/chapkit_ewars_python/` | The Python model as a chapkit service: data layer, INLA primitives, INLA-style inference, service files, run guide |
| `05_pythonModel/01_dataLayer` | L1–L2 against the R reference |
| `05_pythonModel/02_modelPrimitives` | The INLA model pieces against INLA's values, computed in the reference image |
| `05_pythonModel/03_inference/a_laplaceCcd` | Candidate (a): the objective at INLA's points; L3–L4 against every R fit |
| `05_pythonModel/04_throughChap` | L5: the service through chap's backtest; the run guide, run as written |
| `06_closenessReport` | The report |

Candidate (a) follows INLA's compact-mode engine from its C source, archived as
`Archive/r-inla-gmrflib/` and summarised with line citations in
`a_laplaceCcd/results/inla_spec.md`. It reproduces:

- the Laplace objective, with INLA's prior normalisation and the 1e-4 RW1 diagonal;
- the central composite design, with its skewness factors and weights;
- the VB correction of the mean;
- the sampler, which picks configurations by density times weight.

Its departures from INLA (the optimiser, the Hessian's directions, the projection of the
sampling mean) are listed in JC-28.

## What it shows

- **L1–L2.** The frame is exact. The cross-basis agrees to within 4.4e-16, against the
  plan's 1e-8.
- **Model pieces.** The scale factor agrees with INLA's to 1.3e-8 relative and the priors to
  2.4e-12. The objective at INLA's integration points agrees to within 1e-4 log units
  (weekly) and 0.021 (monthly).
- **L3.** Against clean R fits, posterior means shift by a median of at most 0.025 sd for the
  hyperparameters and at most 0.024 sd for latent quantities. Clean R refits differ from each
  other by up to 0.59 sd and 0.09 sd respectively. The hyperparameter modes fall inside the
  range of the clean R modes on every dataset and variant.
- **L4.** Python-vs-R cannot be told apart from R-vs-R or Python-vs-Python: a mean shift of
  about 0.03 sd and a W1 of about 0.05 sd are the Monte Carlo floor of 1000 samples.
- **L5.** Monthly CRPS is 1115.7–1132.1 for Python against 1123.9–1138.0 for R. Weekly it is
  21.95–22.16 against 21.92–22.10. Paired per row, Python-vs-R differences match R-vs-R ones.
  Both models rank the same way against chap's baselines: on the monthly data both are worse
  than seasonal_median (740.7) and persistence (822.5).
- **Behaviour.** The Python fit is deterministic. None of its fits had a VB abort or a dropped
  integration point, and none of its 6 chap evaluations crashed. R flagged 1 of 42 sweep
  fits, and 1 of its 5 monthly evaluations crashed.
- **Cost.** A fit takes 1–11 s natively. A 7-split chap evaluation takes about 2 minutes
  (weekly) or 5–6 minutes (monthly).

## Ledgers

JC-20 to JC-31 and CH-23 to CH-27 were added. CH-24 records a fault in the first R-vs-R
comparison, where replicated random effects were matched on ID; JC-31 corrects a figure that
JC-23 and JC-28 quoted.

## For the human

1. **The report gives no verdict.** Each layer sets Python-vs-R beside R-vs-R; your
   yardstick goes there. The one systematic difference at L3 is small: on two weekly
   variants, the hyperparameters' median shift against R is 0.011–0.028 sd, while R refits
   differ from each other by 0.000–0.018.
2. **On the monthly data, EWARS (R and Python alike) scores worse than two of chap's naive
   baselines.** This finding concerns the model rather than the translation.
3. **Still open**:
   - candidate (b) (MCMC), which would show how much of INLA's own approximation the
     agreement rests on;
   - the stability phase (D), on a compute budget still to be set;
   - the sealed holdout (E).
4. Q1 and Q3 stand with their defaults. Q2 is answered (§4b, 2026-10-17).

## Next

Batch 9, candidate (b), or phase D, at your choice.
