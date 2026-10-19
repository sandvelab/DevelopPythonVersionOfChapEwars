#!/usr/bin/env bash
# Main script for node: b_mcmcNuts
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
# 1. The density NUTS samples against the density candidate (a) approximates.
"$PYTHON" scripts/check_target.py ../../../03_referenceHarness/results ../../../03_referenceHarness/scripts/configs \
  ../../scripts/chapkit_ewars_python results/target_check.tsv > results/check_target.log
# 2. NUTS on the harness inputs: 2 datasets x 4 variants x 3 independent runs, each 4 chains
#    of 1000 warm-up and 1000 kept iterations (JC-33).
rm -rf results/mcmc_fits && mkdir -p results/mcmc_fits
"$PYTHON" scripts/run_mcmc_fits.py ../../../03_referenceHarness/results ../../../03_referenceHarness/scripts/configs \
  ../../scripts/chapkit_ewars_python results/mcmc_fits 3 1000 1000 4 > results/mcmc_fits/run.log
# 3. L3-L4 against every R run, against itself, and against candidate (a).
"$PYTHON" scripts/compare.py results/mcmc_fits/fits ../a_laplaceCcd/results/python_fits/fits \
  ../../../03_referenceHarness/results ../../../04_fidelityMetrics/scripts \
  ../../../04_fidelityMetrics/results/r_fit_health.tsv results > results/compare.log
# 4. The summary tables the answers are read from.
"$PYTHON" scripts/summarise.py results ../a_laplaceCcd/results/python_fits/python_fits_timings.tsv > results/summarise.log
