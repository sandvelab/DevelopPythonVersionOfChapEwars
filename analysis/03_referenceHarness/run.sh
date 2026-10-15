#!/usr/bin/env bash
# Main script for node: 03_referenceHarness
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
# 1. Component seeds, derived from the project seed (readme-at-start.md).
"$PYTHON" scripts/derive_seeds.py 20261014 5 results/seeds.tsv
# 2. Fit inputs: the last 3 periods of each development dataset as the future, in the shape
#    chap hands the model; the weekly history is checked against chap's own workspace file.
rm -rf results/inputs
"$PYTHON" scripts/make_fit_inputs.py ../01_referenceThroughChap/results/run1/inputs \
  ../01_referenceThroughChap/results/run1/weekly_workspace/workspace/historic.csv 3 results/inputs
# 3. The instrumented R reference, inside the reference image (env/README.md):
#    2 datasets x 4 config variants x 5 seeded replicates, plus a seeded repeat.
rm -rf results/fits
caffeinate -i bash scripts/run_fits.sh results/inputs results/seeds.tsv results/fits 2>&1 | tee results/run_fits.log
# 4. The L5 noise floor: the R original through chap, 4 unseeded repeats per dataset.
FRESH=(env -i HOME="$HOME" PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$HOME/.local/bin" bash --noprofile --norc)
rm -rf work/chap_repeats results/chap_repeats
mkdir -p results/chap_repeats
caffeinate -i "${FRESH[@]}" scripts/run_chap_repeats.sh 4 results/chap_repeats work/chap_repeats 2>&1 | tee results/chap_repeats/run.log
# 5. CH-20 diagnostic: the default config fitted 3 times per dataset with INLA single-threaded
#    (not the reference as it runs: tests whether threading causes the refit differences).
rm -rf results/thread_diagnostic
caffeinate -i bash scripts/run_thread_diagnostic.sh results/inputs results/seeds.tsv results/thread_diagnostic 2>&1 | tee results/thread_diagnostic.log
# 6. Tables of what the runs recorded.
"$PYTHON" scripts/summarise_harness.py results
