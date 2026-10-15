result: results/refit_agreement.tsv
script: scripts/summarise_harness.py
        sha256:c9429ba201d4df5c5c9ae010f0a1af7d037b53a8f6e6f33d53e52753905222ee
invocation: step 6 of run.sh: $PYTHON scripts/summarise_harness.py results (> results/summarise.log); re-run at commit eb47134 after the diagnostic
inputs: results/fits/, results/thread_diagnostic/, results/chap_repeats/ (their records)
environment: environment/ (project main)
seeds: none (deterministic)
commit: de28ef4 (scripts as committed before the run); eb47134 (the same script contents, plus the
  diagnostic and summariser changes, committed after they ran — see each record)
instructions-commit: 400536d
node: analysis/03_referenceHarness
produced: 2026-10-15
alternatives-considered: comparing every pair of replicates rather than rep1 against the rest. Rejected: the largest difference against one fixed replicate bounds the spread within a factor of 2 and is simpler to read; batch 5 computes the noise-floor metrics proper.
agency: agent-autonomous
information: -
