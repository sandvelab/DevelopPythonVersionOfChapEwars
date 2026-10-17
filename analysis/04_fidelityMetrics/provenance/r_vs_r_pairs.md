result: (7 files, listed under files:)
script: scripts/describe_r_reference.py
        sha256:fd060425b3990f2966b1818c62c3f9274c82eb3d23cf95edaff189f7b0894804
        scripts/fidelity.py
        sha256:2567b9562e15941b06b0cbf54069d99654f9b676d4af6ea65aeaa2d657784fd5
invocation: run.sh step 3: $PYTHON scripts/describe_r_reference.py ../03_referenceHarness/results results/l5_rows results > results/describe_r_reference.log
inputs:
  ../03_referenceHarness/results/fits  dir-sha256:f08f8fbc0b05c469
  ../03_referenceHarness/results/thread_diagnostic  dir-sha256:b2c8ca3656c8e577
  ../03_referenceHarness/results/chap_repeats/timings.tsv  sha256:561257f9c2ab6b2c
  results/l5_rows  dir-sha256:cc0897d288bdc4af
environment: environment/ (project main)
seeds: none (deterministic)
commit: 96251eb (before run); 77a8482 (scripts as run)
instructions-commit: 400536d
node: analysis/04_fidelityMetrics
produced: 2026-10-17
alternatives-considered: JC-25 gives the measures and their alternatives (absolute differences, KL divergence, a tolerance file); JC-26 the pooling of batch 2's run1 with the chap repeats at L5. The per-row files of replicates 2-5 and of the seeded repeat are read from the local copies JC-18 gitignores; their sha256 are in ../03_referenceHarness/results/fits_manifest.sha256
agency: agent-autonomous
information: -
files:
  results/l3_r_vs_r_pairs.tsv
  results/l3_r_vs_r_quantities.tsv.gz
  results/l4_r_vs_r_pairs.tsv
  results/l4_r_vs_r_rows.tsv.gz
  results/l5_r_vs_r_pairs.tsv
  results/l5_evaluations.tsv
  results/describe_r_reference.log

## 2026-10-17 — fidelity.py changed after this run (comment only)
A docstring line was added stating that it draws no random numbers (the seeds check had
matched the words "random effect"). No code changed; nothing was re-run on it.
script: scripts/fidelity.py
        sha256:322524a62c7397ade5b5b574ba84d406c43ec010bb6cef10b79c3285d0838445
