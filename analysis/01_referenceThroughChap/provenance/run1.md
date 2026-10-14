result: results/run1/chap_core_commit.txt
        results/run1/eval/monthly_ewars__ewars_r.nc
        results/run1/eval/monthly_ewars__global_median.nc
        results/run1/eval/monthly_ewars__persistence.nc
        results/run1/eval/monthly_ewars__seasonal_median.nc
        results/run1/eval/weekly_nicaragua__ewars_r.nc
        results/run1/eval/weekly_nicaragua__global_median.nc
        results/run1/eval/weekly_nicaragua__persistence.nc
        results/run1/eval/weekly_nicaragua__seasonal_median.nc
        results/run1/image_digest.txt
        results/run1/inputs/monthly_ewars.csv
        results/run1/inputs/weekly_nicaragua.csv
        results/run1/metrics/monthly_ewars_metrics.csv
        results/run1/metrics/weekly_nicaragua_metrics.csv
        results/run1/reference_scores.tsv
        results/run1/run.log
        results/run1/service_container.log
        results/run1/service_info.json
        results/run1/timings.tsv
        results/run1/weekly_workspace/artifacts.json
        results/run1/weekly_workspace/inspection.txt
        results/run1/weekly_workspace/workspace/config.yml
        results/run1/weekly_workspace/workspace/data.csv
        results/run1/weekly_workspace/workspace/future.csv
        results/run1/weekly_workspace/workspace/historic.csv
        results/run1/weekly_workspace/workspace/main.py
        results/run1/weekly_workspace/workspace/model.rds
        results/run1/weekly_workspace/workspace/predictions.csv
        results/run1/weekly_workspace/workspace/pyproject.toml
        results/run1/weekly_workspace/workspace/scripts/lib.R
        results/run1/weekly_workspace/workspace/scripts/predict.R
        results/run1/weekly_workspace/workspace/scripts/train.R
        results/run1/weekly_workspace/workspace/uv.lock
script: scripts/run_reference_through_chap.sh
        sha256:89babdc84cda3ad921a4fdb2076af7ff3adf88c134a54ade9618e7a6f6bec669
        scripts/prepare_inputs.py
        sha256:a7487d84659da4199d41846d523454e12f6b476155a08877ca1d6ef471d73015
        scripts/fetch_last_workspace.py
        sha256:f0d2e09d4e51f79c8093aa2f39a65060f8cabc4791193e405918821a48e0f673
        scripts/inspect_workspace.py
        sha256:939f89b18a7693a9e3ee70482d8e65ccdcef99d5b98dcd9cbf1c4f5ff9c7d02f
        scripts/ewars_config.yaml
        sha256:db6143456deba36502ef455d8d468618408641e7222fe47e69b4cb30992dee94
        scripts/backtest_settings.env  sha256:c890f99e011effeb66dd5f0e000b7bf01616985a00a148d2c31184acffe450f2
        scripts/summarise_reference.py (reference_scores.tsv only)
        sha256:cd6f719f14f32331b73aed76a7f97bdc97236b1f0c26dad0412ebe06ad356b5c
invocation: bash analysis/run.sh (step 1 of this node's run.sh):
  env -i HOME=$HOME PATH=/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$HOME/.local/bin bash --noprofile --norc
    scripts/run_reference_through_chap.sh results/run1 work/run1 2>&1 | tee results/run1/run.log
  then (step 4) work/run1/chap-core/.venv/bin/python scripts/summarise_reference.py results/run1
  Every chap command, with all its arguments, is traced in results/run1/run.log.
inputs: ../../Archive/dev-data/monthly_ewars/historic_data.csv  sha256:ec9c37bd05009b85e01c336e743a53d392a984692e32a6f4103bf7dc79861e4b
        ../../Archive/dev-data/weekly_nicaragua/nicaragua_weekly_data_pre2018.csv  sha256:acc52a4effaab82ee8bfd0f465d48ac0642d6f3734ae0a2718b438cb71c4dca8
        derived: results/run1/inputs/monthly_ewars.csv  sha256:da7deebee0779d15ed8240229578564d86151539b8758f58557201535d786e5c
                 results/run1/inputs/weekly_nicaragua.csv  sha256:c72c40fe12d4436f162e186e4ada906b94d10e8eb712764efc2aea0c19c54513
environment: node env/ (chap-core b8c8f788 from its uv.lock, Python 3.13; EWARS image sha256:959fb4f0…c6ff88, linux/amd64 under emulation on Docker 27.4.0, darwin arm64)
seeds: none settable. chap's built-in baselines are deterministic (their spec requires a fixed seed); the R model
  sets no seed and chap passes none, so the EWARS samples are drawn from R's time-seeded RNG (CH-10). Project seed
  20261014 is therefore not applied here; component seeds start with the batch-4 instrumentation.
commit: 687755b (all scripts above as committed, except: run.sh step 4 and scripts/summarise_reference.py were
  written while the run was in progress and committed after it, in the batch-2 closing commit; the digest above is
  the version that ran)
instructions-commit: 400536d
node: analysis/01_referenceThroughChap
produced: 2026-10-14
alternatives-considered: backtest settings, weather provider, input columns, configuration route, baselines,
  image source and chap-core install method are each a judgment call with its alternatives in the JC ledger
  (JC-02 … JC-08). The archived monthly file as-is was run and fails (run1_attempt2_archivedInputs, CH-07).
  A 'run the tutorial only' reference (monthly data only) was not chosen: both code paths, monthly and weekly,
  need a reference (plan §4, Data).
agency: agent-autonomous
information: agent-retrieved (chap-core docs and source at the pinned commit; EWARS README and publish workflow)
