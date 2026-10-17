#!/usr/bin/env bash
# Main script for node: 04_fidelityMetrics
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
# 1. chap-core at the pinned commit, for reading chap's evaluation files (claim.md, Environment).
CHAP_PY="$(bash scripts/ensure_chap_core.sh work)"
# 2. L5 rows: every R evaluation through chap (batch 2's run1 with its baselines, and the
#    chap repeats of 03_referenceHarness) as per-row tables named <dataset>__<model>__<run>.
rm -rf results/l5_rows && mkdir -p results/l5_rows
for f in ../01_referenceThroughChap/results/run1/eval/*.nc; do
  b="$(basename "$f" .nc)"; "$CHAP_PY" scripts/nc_to_rows.py "$f" "results/l5_rows/${b}__run1.tsv"
done
for f in ../03_referenceHarness/results/chap_repeats/eval/*.nc; do
  b="$(basename "$f" .nc)"; "$CHAP_PY" scripts/nc_to_rows.py "$f" "results/l5_rows/${b}.tsv"
done
# 3. The R reference against itself at L3-L5, every fit and evaluation kept.
"$PYTHON" scripts/describe_r_reference.py ../03_referenceHarness/results results/l5_rows results > results/describe_r_reference.log

