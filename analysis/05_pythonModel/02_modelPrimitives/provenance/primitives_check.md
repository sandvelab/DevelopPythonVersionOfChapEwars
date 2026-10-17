result: (4 files, listed under files:)
script: scripts/inla_primitives.R
        sha256:dc4ee9ba3ad006c821b63d320a8b633ed4b01cfceb9cc544e9ccc56197c82cc9
        scripts/check_primitives.py
        sha256:ec6b74179434bc375bdcc7232b76b759ff23de61d9220060153c042d3d030eba
        ../scripts/chapkit_ewars_python/ewars_python/primitives.py
        sha256:17161aba104db63a7d2999c4c7efcee505015854221f4eef20ad3c286713c829
invocation: run.sh: docker run --rm --platform linux/amd64 --user root --entrypoint Rscript -v scripts:/s -v results:/out <reference image> /s/inla_primitives.R /out/inla_values; $PYTHON scripts/check_primitives.py results/inla_values ../scripts/chapkit_ewars_python results/primitives_check.tsv
inputs:
environment: the R reference image ghcr.io/chap-models/chapkit_ewars_model@sha256:959fb4f0f1b9d257a9697925f4500fd8ec4ffa9e1bb3ed7fc36e4f5c57c6ff88 (inla_primitives.R); environment/ (project main) for the check
seeds: set.seed(1) in inla_primitives.R (fixed test inputs; no randomness is drawn)
commit: 77a8482
instructions-commit: 400536d
node: analysis/05_pythonModel/02_modelPrimitives
produced: 2026-10-17
alternatives-considered: Checking the scale factor against the C library's own value: not reachable from R without running a fit; R's inla.scale.model is the cross-check (CH-26). Checking the priors and likelihood inside a full fit: done instead by the objective test in 03_inference/a_laplaceCcd
agency: agent-autonomous
information: agent-retrieved (INLA C sources for the formulas)
files:
  results/inla_values/inla_cyclic_rw1_scale.tsv
  results/inla_values/inla_pc_mgamma.tsv
  results/inla_values/r_dnbinom.tsv
  results/primitives_check.tsv

## 2026-10-17 — primitives.py changed after this run (comment only)
A docstring line was added stating that it draws no random numbers (the seeds check had
matched the words "random walk"). No code changed; nothing was re-run on it.
script: scripts/check_primitives.py
        sha256:df963e55c1b5e056c1e5106981422532d9c68d3b991ad6f969dc4ea61ceef1ab
