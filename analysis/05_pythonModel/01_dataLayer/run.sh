#!/usr/bin/env bash
# Main script for node: 01_dataLayer
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
# 1. L1-L2: the package's data layer against the R reference's frame and cross-basis,
#    every development dataset x config variant.
rm -rf results/frames
"$PYTHON" scripts/compare_frame.py ../../03_referenceHarness/results ../../03_referenceHarness/scripts/configs \
  ../scripts/chapkit_ewars_python results
