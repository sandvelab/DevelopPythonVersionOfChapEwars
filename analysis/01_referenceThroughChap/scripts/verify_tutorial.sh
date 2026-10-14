#!/usr/bin/env bash
# The tutorial's completeness check (plan §6, batch 2): extract every ```bash block of the
# tutorial, in order, into one script; run it in an empty shell in an empty directory;
# then compare what it produced with the reference run (compare_tutorial_run.py).
#
# Usage: verify_tutorial.sh <tutorial.md> <out_dir> <work_dir> <reference_run_dir>
set -euo pipefail
PS4='+ '

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TUTORIAL="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
OUT_DIR="$(mkdir -p "$2" && cd "$2" && pwd)"
WORK_DIR="$(mkdir -p "$3" && cd "$3" && pwd)"
REF_DIR="$(cd "$4" && pwd)"

set -x
awk '/^```bash$/{inside=1; next} /^```$/{inside=0} inside' "$TUTORIAL" > "$OUT_DIR/tutorial_commands.sh"
shasum -a 256 "$TUTORIAL" "$OUT_DIR/tutorial_commands.sh"

cd "$WORK_DIR"
rc=0
env -i HOME="$HOME" PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$HOME/.local/bin" \
  bash --noprofile --norc -x "$OUT_DIR/tutorial_commands.sh" > "$OUT_DIR/tutorial_run.log" 2>&1 || rc=$?
echo "tutorial exit code: $rc" > "$OUT_DIR/tutorial_exit_code.txt"
docker rm -f ewars > /dev/null 2>&1 || true

T="$WORK_DIR/ewars-through-chap"
cp "$T/metrics.csv" "$OUT_DIR/tutorial_metrics.csv" || true
"$T/chap-core/.venv/bin/python" "$SCRIPT_DIR/compare_tutorial_run.py" \
  "$T" "$REF_DIR" "$rc" > "$OUT_DIR/verdict.txt"
cat "$OUT_DIR/verdict.txt"
