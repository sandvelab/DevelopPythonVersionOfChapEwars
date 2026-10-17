# Claim

Can the CHAP-EWARS model be rebuilt in Python, with dlnmpy for the cross-basis and a Python inference engine in place of R-INLA, as a chapkit service that chap-core drives exactly as it drives the R original?

## Children

kind: sub-analyses
main-path: -

## Environment

inherits: the project main environment (`environment/`). The model package in
`scripts/chapkit_ewars_python/` carries its own `pyproject.toml` and `uv.lock` for the
service; they pin the same numpy, scipy, pandas, pyyaml and dlnmpy versions as
`environment/lock.txt`, plus chapkit 2.2.0 (JC-20).

## Answers

1. **Yes.** The package `scripts/chapkit_ewars_python/` is a chapkit service with the R
   original's config schema, data contract and output, and chap-core evaluates it with the same
   commands (04_throughChap answers 1 and 4). Its model frame and cross-basis match R's to
   rounding (01_dataLayer), its model pieces match INLA's (02_modelPrimitives), its fit lands
   inside INLA's own refit-to-refit spread at L3 and L4 (03_inference/a_laplaceCcd), and its chap
   scores overlap the R original's run-to-run range with a similar spread (04_throughChap
   answer 2).
2. **Where it differs from the R original**: its fit is deterministic; none of its 24 harness
   fits had a VB abort or a dropped integration point, and none of its 6 chap evaluations (42
   backtest-split fits) crashed, where INLA flagged 1 of 42 harness fits and crashed in 1 of 5
   monthly evaluations. It runs natively, in about 1-11 s per fit.
