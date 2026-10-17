result: (6 files, listed under files:)
script: ../../04_fidelityMetrics/scripts/nc_to_rows.py
        sha256:f802731e8de2e98890d31ccc1c8d5ec3928ae918d99296ade35f733c26e2d032
        ../../04_fidelityMetrics/scripts/fidelity.py
        sha256:2567b9562e15941b06b0cbf54069d99654f9b676d4af6ea65aeaa2d657784fd5
invocation: run.sh step 2: $CHAP_PY ../../04_fidelityMetrics/scripts/nc_to_rows.py results/chap_runs/eval/<name>.nc results/l5_rows/<name>.tsv
inputs:
  results/chap_runs/eval  dir-sha256:5804759e29f02b12
environment: chap-core b8c8f788 (work/chap-core)
seeds: none (deterministic)
commit: 618c4b3
instructions-commit: 400536d
node: analysis/05_pythonModel/04_throughChap
produced: 2026-10-17
alternatives-considered: As 04_fidelityMetrics/provenance/l5_rows.md
agency: agent-autonomous
information: -
files:
  results/l5_rows/monthly_ewars__ewars_python__run1.tsv
  results/l5_rows/monthly_ewars__ewars_python__run2.tsv
  results/l5_rows/monthly_ewars__ewars_python__run3.tsv
  results/l5_rows/weekly_nicaragua__ewars_python__run1.tsv
  results/l5_rows/weekly_nicaragua__ewars_python__run2.tsv
  results/l5_rows/weekly_nicaragua__ewars_python__run3.tsv

## 2026-10-17 — fidelity.py changed after this run (comment only)
A docstring line was added stating that it draws no random numbers (the seeds check had
matched the words "random effect"). No code changed; nothing was re-run on it.
script: ../../04_fidelityMetrics/scripts/fidelity.py
        sha256:322524a62c7397ade5b5b574ba84d406c43ec010bb6cef10b79c3285d0838445
