#!/usr/bin/env bash
# chap-core at the project's pinned commit, installed from its own lockfile into <work_dir>,
# as node 01 installs it (JC-03). Re-used if already there at the right commit.
# Prints the path of its Python interpreter.
# Usage: ensure_chap_core.sh <work_dir>
set -euo pipefail
WORK_DIR="$(mkdir -p "$1" && cd "$1" && pwd)"
COMMIT=b8c8f788fbc011f3d9d8a18ba9e993725023a6e4
if [ ! -d "$WORK_DIR/chap-core/.git" ] || [ "$(git -C "$WORK_DIR/chap-core" rev-parse HEAD)" != "$COMMIT" ]; then
  rm -rf "$WORK_DIR/chap-core"
  git clone --quiet https://github.com/dhis2-chap/chap-core.git "$WORK_DIR/chap-core" >&2
  git -C "$WORK_DIR/chap-core" checkout --quiet "$COMMIT" >&2
fi
(cd "$WORK_DIR/chap-core" && uv sync --frozen --no-dev --python 3.13 >&2)
echo "$WORK_DIR/chap-core/.venv/bin/python"
