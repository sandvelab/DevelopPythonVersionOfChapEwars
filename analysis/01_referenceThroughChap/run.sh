#!/usr/bin/env bash
# Main script for node: 01_referenceThroughChap
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
# This node's environment is env/: chap-core at its pinned commit, installed from its own
# uv.lock, plus the EWARS image pinned by digest. Both are built by the script itself in a
# fresh shell (env -i), so no interactive environment leaks into the evaluation.
FRESH=(env -i HOME="$HOME" PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$HOME/.local/bin" bash --noprofile --norc)
RUN=run1
rm -rf "work/$RUN"
mkdir -p "results/$RUN"
"${FRESH[@]}" scripts/run_reference_through_chap.sh "results/$RUN" "work/$RUN" 2>&1 | tee "results/$RUN/run.log"
