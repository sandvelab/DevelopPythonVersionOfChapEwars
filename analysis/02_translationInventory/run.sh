#!/usr/bin/env bash
# Main script for node: 02_translationInventory
# Generated shape -- edit the "own scripts" block; the child calls are maintained
# by `node.py rebuild`, which enforces the alternatives/sub-analyses semantics.
set -euo pipefail
cd "$(dirname "$0")"
REPO_ROOT="$(cd "../.." && pwd)"
# Node scripts run under the pinned analysis environment (AGENTS.md §2), not under
# .venv, which is the repository's own machinery. A node needing something beyond it
# declares env/ and overrides PYTHON below.
PYTHON="$REPO_ROOT/environment/env/bin/python"


# Own scripts -- add calls here as scripts/ fills up.
# The R scripts run inside the R reference image (env/README.md): they read what the
# reference actually has installed. build_inventory.py runs under the project environment.
IMG=ghcr.io/chap-models/chapkit_ewars_model@sha256:959fb4f0f1b9d257a9697925f4500fd8ec4ffa9e1bb3ed7fc36e4f5c57c6ff88
RIMG=(docker run --rm --platform linux/amd64 --user root --entrypoint Rscript
      -v "$PWD/scripts:/s:ro" -v "$REPO_ROOT/Archive/chapkit_ewars_model/src/scripts:/src:ro" -v "$PWD/results:/out")
rm -f results/r_calls.tsv results/inla_defaults.tsv results/translation_inventory.md results/coverage.tsv results/unmapped.txt

# 1. Every function call in predict.R, lib.R, train.R, from R's parser, resolved to its package.
"${RIMG[@]}" "$IMG" /s/extract_r_calls.R /src /out/r_calls.tsv
# 2. The INLA settings the fit depends on, from the installed INLA.
"${RIMG[@]}" "$IMG" /s/inla_defaults.R /out/inla_defaults.tsv
# 3. Join with the authored mapping; fails if any call is unmapped.
"$PYTHON" scripts/build_inventory.py .
