result: (6 files, listed under files:)
script: scripts/build_closeness_report.py
        sha256:6c6c20ac27a528184ddb6a15feccdc5d5a0a06507b940a04816e040167ee3dc0
invocation: run.sh: $PYTHON scripts/build_closeness_report.py .. results
inputs:
  ../04_fidelityMetrics/results  dir-sha256:0a0c01120a419f95
  ../05_pythonModel/01_dataLayer/results/l1_l2_comparison.tsv  sha256:9b3484934a74096f
  ../05_pythonModel/02_modelPrimitives/results/primitives_check.tsv  sha256:4b067ba30b9d9aa9
  ../05_pythonModel/03_inference/a_laplaceCcd/results  dir-sha256:dd88c7805677c2fa
  ../05_pythonModel/04_throughChap/results  dir-sha256:c698c554aa0e66ba
environment: environment/ (project main)
seeds: none (deterministic)
commit: built after 618c4b3; script committed with the results in the batch's after-run commit
instructions-commit: 400536d
node: analysis/06_closenessReport
produced: 2026-10-17
alternatives-considered: A verdict per layer: not given (plan §4b, 2026-10-17). Dropping the flagged R fit from the tables: not done; its pairs are shown in their own columns (JC-27)
agency: agent-autonomous
information: -
files:
  results/closeness_report.md
  results/l3_table.tsv
  results/l4_table.tsv
  results/l5_pairs_table.tsv
  results/l5_table.tsv
  results/theta_mode_table.tsv
