result: results/seeds.tsv
script: scripts/derive_seeds.py
        sha256:c8fdc225801b52e860029e26d965cbe135c5db3f6c75f1cc6eae0bd51a9f812d
invocation: step 1 of run.sh: $PYTHON scripts/derive_seeds.py 20261014 5 results/seeds.tsv
inputs: the project seed 20261014 (readme-at-start.md)
environment: environment/ (project main)
seeds: project 20261014; this file is the derivation (components referenceHarness/repK/R and /INLA)
commit: de28ef4 (scripts as committed before the run); eb47134 (the same script contents, plus the
  diagnostic and summariser changes, committed after they ran — see each record)
instructions-commit: 400536d
node: analysis/03_referenceHarness
produced: 2026-10-15
alternatives-considered: one seed per dataset x variant x replicate rather than per replicate. Rejected: shared streams across variants (common random numbers) make variant differences at L4 less noisy; nothing in the plan requires independent streams (JC-17).
agency: agent-autonomous
information: -
