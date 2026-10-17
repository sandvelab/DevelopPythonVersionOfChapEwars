#!/usr/bin/env bash
# Main script for node: 04_throughChap
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
# 1. The Python service through chap's backtest, 3 runs per dataset (EWARS_SEED varied).
FRESH=(env -i HOME="$HOME" PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$HOME/.local/bin" bash --noprofile --norc)
rm -rf results/chap_runs && mkdir -p results/chap_runs
caffeinate -i "${FRESH[@]}" scripts/run_python_through_chap.sh 3 results/chap_runs work 2>&1 | tee results/chap_runs/run.log
# 2. Per-row tables of the evaluations (chap-core's environment, as 04_fidelityMetrics).
CHAP_PY="$(bash ../../04_fidelityMetrics/scripts/ensure_chap_core.sh work)"
rm -rf results/l5_rows && mkdir -p results/l5_rows
for f in results/chap_runs/eval/*.nc; do
  "$CHAP_PY" ../../04_fidelityMetrics/scripts/nc_to_rows.py "$f" "results/l5_rows/$(basename "$f" .nc).tsv"
done
# 3. L5 against the R original's evaluations and chap's baselines.
"$PYTHON" scripts/compare_l5.py results/l5_rows ../../04_fidelityMetrics/results/l5_rows ../../04_fidelityMetrics/scripts results > results/compare_l5.log
# 4. The run guide (the service folder's README.md), run as written from a fresh shell.
rm -rf results/guide_check
bash scripts/verify_guide.sh ../scripts/chapkit_ewars_python/README.md results/guide_check
