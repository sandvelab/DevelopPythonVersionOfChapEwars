#!/usr/bin/env bash
# Main script for node: a_laplaceCcd
# Generated shape -- edit the "own scripts" block; the child calls are maintained
# by `node.py rebuild`, which enforces the alternatives/sub-analyses semantics.
set -euo pipefail
cd "$(dirname "$0")"
REPO_ROOT="$(cd "../../../.." && pwd)"
# Node scripts run under the pinned analysis environment (AGENTS.md §2), not under
# .venv, which is the repository's own machinery. A node needing something beyond it
# declares env/ and overrides PYTHON below.
PYTHON="$REPO_ROOT/environment/env/bin/python"


# Own scripts -- add calls here as scripts/ fills up.
# 1. The Python objective at INLA's own integration points (every R sweep fit).
"$PYTHON" scripts/objective_at_inla_configs.py ../../../03_referenceHarness/results \
  ../../../03_referenceHarness/scripts/configs ../../scripts/chapkit_ewars_python results/objective_at_inla_configs.tsv
# 2. The Python model on the harness inputs: 2 datasets x 4 variants x 3 sampler seeds.
rm -rf results/python_fits && mkdir -p results/python_fits
"$PYTHON" scripts/run_python_fits.py ../../../03_referenceHarness/results ../../../03_referenceHarness/scripts/configs \
  ../../scripts/chapkit_ewars_python results/python_fits 3 > results/python_fits/run.log
# 3. L3-L4 against every R run, with 04_fidelityMetrics' measures.
"$PYTHON" scripts/compare_with_r.py results/python_fits/fits ../../../03_referenceHarness/results \
  ../../../04_fidelityMetrics/scripts ../../../04_fidelityMetrics/results/r_fit_health.tsv results > results/compare_with_r.log
