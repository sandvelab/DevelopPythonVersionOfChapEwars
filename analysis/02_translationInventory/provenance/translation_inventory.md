result: results/translation_inventory.md
        results/coverage.tsv
        results/unmapped.txt
script: scripts/build_inventory.py
        sha256:0fe135dac6d861044a7b57eac5a7c145b349d41bf99b2d6120bb764b7dd2fec0
        scripts/call_mapping.tsv  sha256:53c69c93d28e283d661a9c20ff0d8b8f3eba60b1432702ee937592ff5c136f35
invocation: step 3 of run.sh: environment/env/bin/python scripts/build_inventory.py .
inputs: results/r_calls.tsv, results/inla_defaults.tsv (this node), scripts/call_mapping.tsv (authored)
environment: environment/ (project main; Python 3.13.0, pandas 3.0.6)
seeds: none (deterministic)
commit: b534c59
instructions-commit: 400536d
node: analysis/02_translationInventory
produced: 2026-10-14
alternatives-considered: writing the inventory by hand as prose. Rejected: the join makes completeness
  checkable (unmapped.txt must be empty, and the script fails otherwise). The Python column, status,
  batch and notes in call_mapping.tsv are the agent's judgment, grounded in the archived sources cited
  in each note; they are not mechanically derived. Status 'counterpart-verify' and 'gap-port' rows are
  verified against R output in the batch named before any use (plan §1).
agency: agent-autonomous (the mapping); information: agent-retrieved (Archive/r-sources, Archive/dlnmpy,
  Archive/python-inla-candidates)
