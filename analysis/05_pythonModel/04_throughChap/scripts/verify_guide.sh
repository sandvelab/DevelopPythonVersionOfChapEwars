#!/usr/bin/env bash
# The run guide's check: extract every ```bash block of the service folder's README.md, in
# order, into one script, and run it in an empty shell from the repository root, as a user
# would. The log shows each command and its output, including chap's scores.
#
# Usage: verify_guide.sh <README.md> <out_dir>
set -euo pipefail
PS4='+ '
GUIDE="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
OUT_DIR="$(mkdir -p "$2" && cd "$2" && pwd)"
REPO_ROOT="$(git -C "$(dirname "$GUIDE")" rev-parse --show-toplevel)"
awk '/^```bash$/{inside=1; next} /^```$/{inside=0} inside' "$GUIDE" > "$OUT_DIR/guide_commands.sh"
shasum -a 256 "$GUIDE" "$OUT_DIR/guide_commands.sh" > "$OUT_DIR/guide_sha256.txt"
cd "$REPO_ROOT"
rc=0
env -i HOME="$HOME" PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$HOME/.local/bin" \
  bash --noprofile --norc -x "$OUT_DIR/guide_commands.sh" > "$OUT_DIR/guide_run.log" 2>&1 || rc=$?
docker rm -f ewars-python > /dev/null 2>&1 || true
echo "guide exit code: $rc" | tee "$OUT_DIR/guide_exit_code.txt"
exit "$rc"
