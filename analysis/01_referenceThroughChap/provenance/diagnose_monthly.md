result: results/diagnose_monthly/as_archived.chap.log
        results/diagnose_monthly/canonical_columns.chap.log
        results/diagnose_monthly/canonical_columns.nc
        results/diagnose_monthly/failed_predict_workspace.zip
        results/diagnose_monthly/failed_predict_workspace/config.yml
        results/diagnose_monthly/failed_predict_workspace/data.csv
        results/diagnose_monthly/failed_predict_workspace/future.csv
        results/diagnose_monthly/failed_predict_workspace/historic.csv
        results/diagnose_monthly/failed_predict_workspace/main.py
        results/diagnose_monthly/failed_predict_workspace/model.rds
        results/diagnose_monthly/failed_predict_workspace/pyproject.toml
        results/diagnose_monthly/failed_predict_workspace/scripts/lib.R
        results/diagnose_monthly/failed_predict_workspace/scripts/predict.R
        results/diagnose_monthly/failed_predict_workspace/scripts/train.R
        results/diagnose_monthly/failed_predict_workspace/uv.lock
        results/diagnose_monthly/monthly_canonical_columns.csv
        results/diagnose_monthly/outcomes.txt
        results/diagnose_monthly/service_container.log
        results/diagnose_monthly/workspace_inspection.txt
        results/diagnose_monthly.log
script: scripts/diagnose_monthly_failure.sh
        sha256:279d0d9b99acc8d18f269189a5a3dd08dedc4b267e0d1ff1be179ecb234a0bf1
        scripts/inspect_workspace.py
        sha256:939f89b18a7693a9e3ee70482d8e65ccdcef99d5b98dcd9cbf1c4f5ff9c7d02f
        scripts/ewars_config.yaml
        sha256:db6143456deba36502ef455d8d468618408641e7222fe47e69b4cb30992dee94
invocation: step 2 of this node's run.sh:
  env -i ... bash --noprofile --norc scripts/diagnose_monthly_failure.sh results/diagnose_monthly
    work/run1/chap-core/.venv 2>&1 | tee results/diagnose_monthly.log
inputs: ../../Archive/dev-data/monthly_ewars/historic_data.csv  sha256:ec9c37bd05009b85e01c336e743a53d392a984692e32a6f4103bf7dc79861e4b
environment: node env/ (chap-core b8c8f788 from its uv.lock, Python 3.13; EWARS image sha256:959fb4f0…c6ff88, linux/amd64 under emulation on Docker 27.4.0, darwin arm64)
seeds: none settable (CH-10); the outcome checked is pass/fail, not a score
commit: 687755b
instructions-commit: 400536d
node: analysis/01_referenceThroughChap
produced: 2026-10-14
alternatives-considered: reading the failure from the error message alone (it names ID_time_cyclic but not why it
  is non-integer); patching predict.R to bypass inla.check.location (forbidden: the original is never modified,
  plan §3); switching to the `observed` weather provider (changes the backtest, JC-04). Downloading the failed
  job's workspace shows the actual data R received, which settles the cause from a file.
agency: agent-autonomous
information: agent-retrieved (chapkit artifact API, Archive/chapkit/src/docs/guides/artifact-storage.md)
