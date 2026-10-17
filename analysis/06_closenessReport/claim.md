# Claim

How close is the Python model's behaviour to the R reference's at each fidelity layer, set beside the R reference's own run-to-run behaviour as it runs?

## Children

kind: -
main-path: -

## Environment

inherits: the project main environment (`environment/`)

## Answers

1. **The report is `results/closeness_report.md`.** It applies no threshold: every layer sets
   the Python-vs-R distance beside the R-vs-R distance on the same measures, with the flagged R
   fit's pairs in their own columns.
2. On L1-L4 and in both datasets, the Python-vs-R figures lie within or at the edge of the
   range of the clean R-vs-R figures (`results/l3_table.tsv`, `l4_table.tsv`); at L5 the Python
   runs' CRPS overlaps the R runs' range, one monthly run below it and one weekly run above
   it, and the paired per-row differences match the R-vs-R ones (`results/l5_table.tsv`,
   `l5_pairs_table.tsv`). The one systematic exception at L3 is small: on the weekly default and
   no-covariates variants the hyperparameters' median shift against clean R fits is 0.011-0.028
   posterior sd, against 0.000-0.018 between R fits (`results/l3_table.tsv`).
