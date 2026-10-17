result: (10 files, listed under files:)
script: scripts/compare_frame.py
        sha256:4ccc72489fd17032afecf8c73ed2b33043ea2a1297fe78709fed5a4f72bd6d05
        ../scripts/chapkit_ewars_python/ewars_python/frame.py
        sha256:7b593a88a125bd95595f86b2bb82756b19184b80950f7ba12f50d04cdebe8f36
invocation: run.sh: $PYTHON scripts/compare_frame.py ../../03_referenceHarness/results ../../03_referenceHarness/scripts/configs ../scripts/chapkit_ewars_python results
inputs:
  ../../03_referenceHarness/results/inputs  dir-sha256:d8eb202263e8d4a8
  ../../03_referenceHarness/scripts/configs  dir-sha256:12d66d5d0b3843f8
  ../../03_referenceHarness/results/fits/monthly_ewars/default/rep1/model_frame.csv.gz  sha256:186f011ecf05e1f7
  ../../03_referenceHarness/results/fits/weekly_nicaragua/default/rep1/model_frame.csv.gz  sha256:dc814504e26a4001
environment: environment/ (project main)
seeds: none (deterministic)
commit: 77a8482
instructions-commit: 400536d
node: analysis/05_pythonModel/01_dataLayer
produced: 2026-10-17
alternatives-considered: Comparing against R's frame from every replicate: unnecessary, L1-L2 are identical across R refits (03_referenceHarness answer 1). Absolute tolerance per column: none is applied (plan §4b, 2026-10-17); the differences are reported. JC-21 (location order), CH-25 (round-trip float parsing)
agency: agent-autonomous
information: -
files:
  results/l1_l2_comparison.tsv
  results/l1_l2_columns.tsv
  results/frames/frame_monthly_ewars_default.csv.gz
  results/frames/frame_monthly_ewars_nlags_3_6.csv.gz
  results/frames/frame_monthly_ewars_no_covariates.csv.gz
  results/frames/frame_monthly_ewars_region_seasonal.csv.gz
  results/frames/frame_weekly_nicaragua_default.csv.gz
  results/frames/frame_weekly_nicaragua_nlags_3_6.csv.gz
  results/frames/frame_weekly_nicaragua_no_covariates.csv.gz
  results/frames/frame_weekly_nicaragua_region_seasonal.csv.gz
