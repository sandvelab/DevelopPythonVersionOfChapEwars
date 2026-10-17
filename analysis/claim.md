# Claim

How closely can a Python translation of the CHAP-EWARS model (R-INLA + `dlnm`, with `dlnmpy`
replacing `dlnm`) reproduce the R original's probabilistic forecasts when both are run
through chap-core on identical data and backtests — relative to the R original's own
seed-to-seed variability — and which translation choices drive any difference?

## Children

kind: sub-analyses
main-path: -

## Environment

inherits: the project main environment (`environment/`), pinned in batch 3; nodes that
need more declare it in their own claim.md.

## Answers

1. **On the development data, the Python translation reproduces the R original as closely as
   the R original reproduces itself**, at every layer, without a threshold being applied
   (06_closenessReport answers 1-2): the frame and cross-basis to rounding, the posterior and
   predictive distributions within the spread of INLA's own refits, and chap's CRPS overlapping
   the R original's run-to-run range on both datasets, with a similar seed-to-seed spread.
2. **Which translation choices drive the remaining difference** is not yet established: the
   stability phase (D) and candidate (b) have not run. The Python engine's departures from
   INLA's are logged in JC-28.
