result: results/objective_at_inla_configs.tsv
script: scripts/objective_at_inla_configs.py
        sha256:6aafa61788f4d0dba7fac11cd9711bd1e3ca0283cc6f80749dd6f6759a005b53
        ../../scripts/chapkit_ewars_python/ewars_python/frame.py
        sha256:7b593a88a125bd95595f86b2bb82756b19184b80950f7ba12f50d04cdebe8f36
        ../../scripts/chapkit_ewars_python/ewars_python/latent.py
        sha256:d9763fdc950c359b818db315c2933b6f0a8c9de9165e368f547afc0a27103ef2
        ../../scripts/chapkit_ewars_python/ewars_python/laplace.py
        sha256:a1d5bf8e8c2554f1c47b5910608aad5ba5c8f383d31e1fe4c8ffe0eab8b09252
        ../../scripts/chapkit_ewars_python/ewars_python/primitives.py
        sha256:17161aba104db63a7d2999c4c7efcee505015854221f4eef20ad3c286713c829
invocation: run.sh step 1: $PYTHON scripts/objective_at_inla_configs.py ../../../03_referenceHarness/results ../../../03_referenceHarness/scripts/configs ../../scripts/chapkit_ewars_python results/objective_at_inla_configs.tsv
inputs:
  ../../../03_referenceHarness/results/fits  dir-sha256:f08f8fbc0b05c469
  ../../../03_referenceHarness/results/inputs  dir-sha256:d8eb202263e8d4a8
environment: environment/ (project main)
seeds: none (deterministic)
commit: 77a8482
instructions-commit: 400536d
node: analysis/05_pythonModel/03_inference/a_laplaceCcd
produced: 2026-10-17
alternatives-considered: Comparing only the modes: confounds the objective with the mode search; evaluating at INLA's own points separates them
agency: agent-autonomous
information: -

## 2026-10-17 — primitives.py changed after this run (comment only)
A docstring line was added stating that it draws no random numbers (the seeds check had
matched the words "random walk"). No code changed; nothing was re-run on it.
script: ../../scripts/chapkit_ewars_python/ewars_python/primitives.py
        sha256:df963e55c1b5e056c1e5106981422532d9c68d3b991ad6f969dc4ea61ceef1ab
