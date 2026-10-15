result: results/chap_repeats/chap_core_commit.txt
        results/chap_repeats/eval/monthly_ewars__ewars_r__rep2.nc
        results/chap_repeats/eval/monthly_ewars__ewars_r__rep3.nc
        results/chap_repeats/eval/monthly_ewars__ewars_r__rep4.nc
        results/chap_repeats/eval/weekly_nicaragua__ewars_r__rep1.nc
        results/chap_repeats/eval/weekly_nicaragua__ewars_r__rep2.nc
        results/chap_repeats/eval/weekly_nicaragua__ewars_r__rep3.nc
        results/chap_repeats/eval/weekly_nicaragua__ewars_r__rep4.nc
        results/chap_repeats/metrics/monthly_ewars_metrics.csv
        results/chap_repeats/metrics/weekly_nicaragua_metrics.csv
        results/chap_repeats/run.log
        results/chap_repeats/service_container.log
        results/chap_repeats/service_info.json
        results/chap_repeats/timings.tsv
script: scripts/run_chap_repeats.sh
        sha256:300596c6930ee232fb098098ad4c319d3954a9854b670f693717d0776ab884f7
invocation: step 4 of run.sh: env -i ... bash --noprofile --norc scripts/run_chap_repeats.sh 4 results/chap_repeats work/chap_repeats (ran without the caffeinate prefix, CH-21)
inputs: ../01_referenceThroughChap/results/run1/inputs/*.csv (hashes in inputs.md and in chap_repeats/run.log); ../01_referenceThroughChap/scripts/ewars_config.yaml sha256:db6143456deba36502ef455d8d468618408641e7222fe47e69b4cb30992dee94; ../01_referenceThroughChap/scripts/backtest_settings.env sha256:c890f99e011effeb66dd5f0e000b7bf01616985a00a148d2c31184acffe450f2
environment: node env/: chap-core b8c8f788 from its uv.lock (work/chap_repeats/chap-core/.venv); the reference image ghcr.io/chap-models/chapkit_ewars_model@sha256:959fb4f0f1b9d257a9697925f4500fd8ec4ffa9e1bb3ed7fc36e4f5c57c6ff88
seeds: none possible (CH-10): the R reference is unseeded through chap; the spread across repeats is the quantity measured
commit: de28ef4 (scripts as committed before the run); eb47134 (the same script contents, plus the
  diagnostic and summariser changes, committed after they ran — see each record)
instructions-commit: 400536d
node: analysis/03_referenceHarness
produced: 2026-10-15
alternatives-considered: (a) 2 repeats, the plan's minimum. Rejected: with a 3-period horizon and 7 splits, 2 values say little about a spread; 4 per dataset cost ~40 min. (b) re-running the baselines too. Rejected: they are deterministic (JC-19). Monthly repeat 1 produced no evaluation: INLA crashed in one split (CH-20); kept, and not re-run.
agency: agent-autonomous
information: -
