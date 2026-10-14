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
# uv.lock, plus the EWARS image pinned by digest. The scripts build both themselves, each in
# a fresh shell (env -i), so no interactive environment leaks into the evaluation.
FRESH=(env -i HOME="$HOME" PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$HOME/.local/bin" bash --noprofile --norc)

# 1. The reference scores: EWARS (R) and chap's built-in baselines, both dev datasets.
RUN=run1
rm -rf "work/$RUN" "results/$RUN"
mkdir -p "results/$RUN"
"${FRESH[@]}" scripts/run_reference_through_chap.sh "results/$RUN" "work/$RUN" 2>&1 | tee "results/$RUN/run.log"

# 2. CH-07: why the archived monthly file fails, with the chap-core environment of step 1.
rm -rf results/diagnose_monthly
"${FRESH[@]}" scripts/diagnose_monthly_failure.sh results/diagnose_monthly "work/$RUN/chap-core/.venv" 2>&1 | tee results/diagnose_monthly.log

# 3. The tutorial, run verbatim in an empty shell and compared with step 1.
rm -rf work/tutorial_check results/tutorial_check
"${FRESH[@]}" scripts/verify_tutorial.sh "$REPO_ROOT/AI-generated/26-10-14_tutorialRunOriginalEwarsThroughChap.md" \
  results/tutorial_check work/tutorial_check "results/$RUN" 2>&1 | tee results/tutorial_check.log

# 4. One table of the reference scores and times, from chap's metric files.
"work/$RUN/chap-core/.venv/bin/python" scripts/summarise_reference.py "results/$RUN"
