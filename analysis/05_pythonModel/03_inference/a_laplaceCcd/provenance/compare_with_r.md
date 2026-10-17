result: (5 files, listed under files:)
script: scripts/compare_with_r.py
        sha256:7b7b7819cf45cd3b9010153e7ec54ed7162692cc446f922f2e7f1e6fe61bc90d
        ../../../04_fidelityMetrics/scripts/fidelity.py
        sha256:2567b9562e15941b06b0cbf54069d99654f9b676d4af6ea65aeaa2d657784fd5
invocation: run.sh step 3: $PYTHON scripts/compare_with_r.py results/python_fits/fits ../../../03_referenceHarness/results ../../../04_fidelityMetrics/scripts ../../../04_fidelityMetrics/results/r_fit_health.tsv results > results/compare_with_r.log
inputs:
  results/python_fits/fits  dir-sha256:5ba7b6c1a33852b6
  ../../../03_referenceHarness/results/fits  dir-sha256:f08f8fbc0b05c469
  ../../../04_fidelityMetrics/results/r_fit_health.tsv  sha256:e438667444b7320d
environment: environment/ (project main)
seeds: none (deterministic)
commit: 77a8482
instructions-commit: 400536d
node: analysis/05_pythonModel/03_inference/a_laplaceCcd
produced: 2026-10-17
alternatives-considered: JC-25 (measures). Every R run is kept, each pair labelled by the R run's health (plan §4b, 2026-10-17)
agency: agent-autonomous
information: -
files:
  results/l3_python_vs_r_pairs.tsv
  results/l3_python_vs_r_quantities.tsv.gz
  results/l4_python_vs_r_pairs.tsv
  results/l4_python_vs_r_rows.tsv.gz
  results/compare_with_r.log

## 2026-10-17 — fidelity.py changed after this run (comment only)
A docstring line was added stating that it draws no random numbers (the seeds check had
matched the words "random effect"). No code changed; nothing was re-run on it.
script: ../../../04_fidelityMetrics/scripts/fidelity.py
        sha256:322524a62c7397ade5b5b574ba84d406c43ec010bb6cef10b79c3285d0838445
