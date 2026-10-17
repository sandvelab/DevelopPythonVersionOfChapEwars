# Claim

Do the Python ports of the INLA model pieces (the scaled cyclic RW1, the constraints, iid with replicate, the negative-binomial likelihood and INLA's default priors) reproduce the values INLA uses?

## Children

kind: -
main-path: -

## Environment

inherits: the project main environment (`environment/`) for `check_primitives.py`;
override: `inla_primitives.R` runs inside the R reference image
(`ghcr.io/chap-models/chapkit_ewars_model@sha256:959fb4f0…c6ff88`), because the values it
checks against are those the reference's own INLA and R compute.

## Answers

1. **The ports reproduce INLA's values** (`results/primitives_check.tsv`): the cyclic RW1
   scale factor for 12, 52 and 53 nodes agrees with R's inla.scale.model to 1.3e-8 relative (the
   C library adds sqrt(DBL_EPSILON) to the diagonal, CH-26); the pc.mgamma log density on log
   size agrees with INLA's to 2.4e-12; the negative-binomial log likelihood with R's dnbinom to
   5.9e-11. The constraint basis is orthonormal and sums to zero to 1.2e-15.
