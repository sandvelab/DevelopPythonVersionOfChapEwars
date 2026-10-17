# Claim

Does the Python data layer reproduce the R reference's model frame (L1) and cross-basis matrices (L2) on every development dataset and config variant?

## Children

kind: -
main-path: -

## Environment

inherits: the project main environment (`environment/`)

## Answers

1. **L1 is exact and L2 is at rounding level** on both datasets and all four variants
   (`results/l1_l2_comparison.tsv`): the frame's numeric columns differ from R's by 0 (monthly)
   and 6.8e-21 (weekly), with no string or missing-value mismatches; the cross-basis matrices
   by at most 4.4e-16, against the plan's 1e-8; knots and boundary knots agree to the 15 digits
   R wrote them with. The same 113 (monthly) and 60 (weekly) rows are predicted.
2. dlnmpy needed no parallel port for this model's specification.
