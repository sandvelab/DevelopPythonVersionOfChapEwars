#!/usr/bin/env bash
# Main script for node: 02_modelPrimitives
# Generated shape -- edit the "own scripts" block; the child calls are maintained
# by `node.py rebuild`, which enforces the alternatives/sub-analyses semantics.
set -euo pipefail
cd "$(dirname "$0")"
REPO_ROOT="$(cd "../../.." && pwd)"
# Node scripts run under the pinned analysis environment (AGENTS.md §2), not under
# .venv, which is the repository's own machinery. A node needing something beyond it
# declares env/ and overrides PYTHON below.
PYTHON="$REPO_ROOT/environment/env/bin/python"


# Own scripts -- add calls here as scripts/ fills up.
# 1. INLA's own values, computed in the R reference image (claim.md, Environment).
IMG=ghcr.io/chap-models/chapkit_ewars_model@sha256:959fb4f0f1b9d257a9697925f4500fd8ec4ffa9e1bb3ed7fc36e4f5c57c6ff88
rm -rf results/inla_values
docker run --rm --platform linux/amd64 --user root --entrypoint Rscript \
  -v "$PWD/scripts:/s:ro" -v "$PWD/results:/out" "$IMG" /s/inla_primitives.R /out/inla_values
# 2. The Python primitives against them.
"$PYTHON" scripts/check_primitives.py results/inla_values ../scripts/chapkit_ewars_python results/primitives_check.tsv
