result: (15 files, listed under files:)
script: scripts/nc_to_rows.py
        sha256:f802731e8de2e98890d31ccc1c8d5ec3928ae918d99296ade35f733c26e2d032
        scripts/fidelity.py
        sha256:2567b9562e15941b06b0cbf54069d99654f9b676d4af6ea65aeaa2d657784fd5
        scripts/ensure_chap_core.sh
        sha256:e70d0939a800d705a6b8d4f6995a1151a1e844ce009a98526102bbf5ff813772
invocation: run.sh steps 1-2: CHAP_PY=$(bash scripts/ensure_chap_core.sh work); $CHAP_PY scripts/nc_to_rows.py <eval.nc> results/l5_rows/<dataset>__<model>__<run>.tsv, for every .nc in ../01_referenceThroughChap/results/run1/eval/ (run1) and ../03_referenceHarness/results/chap_repeats/eval/
inputs:
  ../01_referenceThroughChap/results/run1/eval  dir-sha256:d51244772b4cebf2
  ../03_referenceHarness/results/chap_repeats/eval  dir-sha256:baab3ab73b32e0a9
environment: chap-core b8c8f788 from its uv.lock (work/chap-core; claim.md, Environment)
seeds: none (deterministic)
commit: 96251eb (before run); 77a8482 (scripts as run: fidelity.py keys replicated IDs by position, CH-24, changed after the first run)
instructions-commit: 400536d
node: analysis/04_fidelityMetrics
produced: 2026-10-17
alternatives-considered: Reading per-row metrics from chap's export-metrics instead of recomputing CRPS from the samples. Not done: export-metrics aggregates; the per-row sample CRPS here reproduces chap's aggregate crps exactly (weekly rep1: 21.9186 against 21.918569)
agency: agent-autonomous
information: -
files:
  results/l5_rows/monthly_ewars__ewars_r__rep2.tsv
  results/l5_rows/monthly_ewars__ewars_r__rep3.tsv
  results/l5_rows/monthly_ewars__ewars_r__rep4.tsv
  results/l5_rows/monthly_ewars__ewars_r__run1.tsv
  results/l5_rows/monthly_ewars__global_median__run1.tsv
  results/l5_rows/monthly_ewars__persistence__run1.tsv
  results/l5_rows/monthly_ewars__seasonal_median__run1.tsv
  results/l5_rows/weekly_nicaragua__ewars_r__rep1.tsv
  results/l5_rows/weekly_nicaragua__ewars_r__rep2.tsv
  results/l5_rows/weekly_nicaragua__ewars_r__rep3.tsv
  results/l5_rows/weekly_nicaragua__ewars_r__rep4.tsv
  results/l5_rows/weekly_nicaragua__ewars_r__run1.tsv
  results/l5_rows/weekly_nicaragua__global_median__run1.tsv
  results/l5_rows/weekly_nicaragua__persistence__run1.tsv
  results/l5_rows/weekly_nicaragua__seasonal_median__run1.tsv

## 2026-10-17 — fidelity.py changed after this run (comment only)
A docstring line was added stating that it draws no random numbers (the seeds check had
matched the words "random effect"). No code changed; nothing was re-run on it.
script: scripts/fidelity.py
        sha256:322524a62c7397ade5b5b574ba84d406c43ec010bb6cef10b79c3285d0838445
