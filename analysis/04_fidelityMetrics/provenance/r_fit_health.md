result: (2 files, listed under files:)
script: scripts/describe_r_reference.py
        sha256:fd060425b3990f2966b1818c62c3f9274c82eb3d23cf95edaff189f7b0894804
        scripts/fidelity.py
        sha256:2567b9562e15941b06b0cbf54069d99654f9b676d4af6ea65aeaa2d657784fd5
invocation: run.sh step 3: $PYTHON scripts/describe_r_reference.py ../03_referenceHarness/results results/l5_rows results > results/describe_r_reference.log
inputs:
  ../03_referenceHarness/results/fit_summary.tsv  sha256:7185fb3bd7af701e
environment: environment/ (project main)
seeds: none (deterministic)
commit: 96251eb (before run); 77a8482 (scripts as run)
instructions-commit: 400536d
node: analysis/04_fidelityMetrics
produced: 2026-10-17
alternatives-considered: Excluding flagged fits (reading 2 of the batch 4 report), rejected by the human (plan §4b, 2026-10-17). Flagging any shortfall of integration points instead of fewer than half: two fits lost one point (monthly default rep4, 14 of 15; monthly region_seasonal rep3, 24 of 25), with no VB abort and mode status 0, and are labelled clean; the threshold is recorded in JC-27 so that a reader can relabel them from r_fit_health.tsv
agency: agent-on-human-assessment
information: -
files:
  results/r_fit_health.tsv
  results/r_fit_health_counts.tsv

## 2026-10-17 — fidelity.py changed after this run (comment only)
A docstring line was added stating that it draws no random numbers (the seeds check had
matched the words "random effect"). No code changed; nothing was re-run on it.
script: scripts/fidelity.py
        sha256:322524a62c7397ade5b5b574ba84d406c43ec010bb6cef10b79c3285d0838445
