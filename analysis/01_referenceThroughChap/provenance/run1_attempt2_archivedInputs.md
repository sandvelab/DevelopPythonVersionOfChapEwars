result: results/run1_attempt2_archivedInputs/chap_core_commit.txt
        results/run1_attempt2_archivedInputs/eval/monthly_ewars__global_median.nc
        results/run1_attempt2_archivedInputs/eval/monthly_ewars__persistence.nc
        results/run1_attempt2_archivedInputs/eval/monthly_ewars__seasonal_median.nc
        results/run1_attempt2_archivedInputs/eval/weekly_nicaragua__ewars_r.nc
        results/run1_attempt2_archivedInputs/eval/weekly_nicaragua__global_median.nc
        results/run1_attempt2_archivedInputs/eval/weekly_nicaragua__persistence.nc
        results/run1_attempt2_archivedInputs/eval/weekly_nicaragua__seasonal_median.nc
        results/run1_attempt2_archivedInputs/image_digest.txt
        results/run1_attempt2_archivedInputs/metrics/monthly_ewars_metrics.csv
        results/run1_attempt2_archivedInputs/metrics/weekly_nicaragua_metrics.csv
        results/run1_attempt2_archivedInputs/run.log
        results/run1_attempt2_archivedInputs/service_container.log
        results/run1_attempt2_archivedInputs/service_info.json
        results/run1_attempt2_archivedInputs/timings.tsv
        results/diagnose_monthly_attempt2/as_archived.chap.log
        results/diagnose_monthly_attempt2/canonical_columns.chap.log
        results/diagnose_monthly_attempt2/canonical_columns.nc
        results/diagnose_monthly_attempt2/failed_predict_workspace.zip
        results/diagnose_monthly_attempt2/failed_predict_workspace/config.yml
        results/diagnose_monthly_attempt2/failed_predict_workspace/data.csv
        results/diagnose_monthly_attempt2/failed_predict_workspace/future.csv
        results/diagnose_monthly_attempt2/failed_predict_workspace/historic.csv
        results/diagnose_monthly_attempt2/failed_predict_workspace/main.py
        results/diagnose_monthly_attempt2/failed_predict_workspace/model.rds
        results/diagnose_monthly_attempt2/failed_predict_workspace/pyproject.toml
        results/diagnose_monthly_attempt2/failed_predict_workspace/scripts/lib.R
        results/diagnose_monthly_attempt2/failed_predict_workspace/scripts/predict.R
        results/diagnose_monthly_attempt2/failed_predict_workspace/scripts/train.R
        results/diagnose_monthly_attempt2/failed_predict_workspace/uv.lock
        results/diagnose_monthly_attempt2/monthly_canonical_columns.csv
        results/diagnose_monthly_attempt2/outcomes.txt
        results/diagnose_monthly_attempt2/run.log
        results/diagnose_monthly_attempt2/service_container.log
        results/diagnose_monthly_attempt2/workspace_inspection.txt
script: scripts/run_reference_through_chap.sh
        sha256:c48de24f502cc4110ffab37f0ca6e0f3b8821c45743a6e7f250688501ac03fb6 (version at fa74b72)
        scripts/diagnose_monthly_failure.sh (diagnose_monthly_attempt2/ only)
        sha256:279d0d9b99acc8d18f269189a5a3dd08dedc4b267e0d1ff1be179ecb234a0bf1
        scripts/inspect_workspace.py
        sha256:939f89b18a7693a9e3ee70482d8e65ccdcef99d5b98dcd9cbf1c4f5ff9c7d02f
        scripts/ewars_config.yaml
        sha256:db6143456deba36502ef455d8d468618408641e7222fe47e69b4cb30992dee94
        scripts/backtest_settings.env  sha256:c961bdea91d4769e3ceb9827c9f0bd3eba4edb942eb3fef3e9895cb82da37d76 (version at fa74b72)
invocation: bash analysis/01_referenceThroughChap/run.sh at commit fa74b72 (writing to results/run1 and
  results/diagnose_monthly, renamed before the final run)
inputs: ../../Archive/dev-data/monthly_ewars/historic_data.csv  sha256:ec9c37bd05009b85e01c336e743a53d392a984692e32a6f4103bf7dc79861e4b
        ../../Archive/dev-data/weekly_nicaragua/nicaragua_weekly_data_pre2018.csv  sha256:acc52a4effaab82ee8bfd0f465d48ac0642d6f3734ae0a2718b438cb71c4dca8
environment: node env/ (chap-core b8c8f788 from its uv.lock, Python 3.13; EWARS image sha256:959fb4f0…c6ff88, linux/amd64 under emulation on Docker 27.4.0, darwin arm64)
seeds: none settable (CH-10)
commit: fa74b72
instructions-commit: 400536d
node: analysis/01_referenceThroughChap
produced: 2026-10-14
alternatives-considered: deleting it once superseded. Kept: it is the evaluation of the archived files as they are,
  the evidence for CH-07 (monthly EWARS fails, exit 1) and for the weekly file needing no change. Its weekly EWARS
  scores are a second unseeded run on input identical in content to run1's (the weekly file carries only contract
  columns), usable in batch 4. The backtest used chap's default weather provider, which is climatology, as in run1.
agency: agent-autonomous

## Since: the scripts changed
At 687755b the run script gained the input reduction (JC-05), the explicit weather provider (JC-04) and the
workspace capture (CH-06), and backtest_settings.env gained FUTURE_WEATHER_PROVIDER. Current versions:
script: scripts/run_reference_through_chap.sh
        sha256:89babdc84cda3ad921a4fdb2076af7ff3adf88c134a54ade9618e7a6f6bec669
        scripts/backtest_settings.env  sha256:c890f99e011effeb66dd5f0e000b7bf01616985a00a148d2c31184acffe450f2
They produced run1.
