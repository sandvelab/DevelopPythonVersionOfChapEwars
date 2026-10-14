#!/usr/bin/env bash
# Archive the evidence for the plan's inference candidate (c), "an existing Python INLA
# implementation" (batch 3). Found by web search on 2026-10-14 (agent-retrieved):
#   pyinla  — PyPI metadata only: its declared licence is "Proprietary", so its files are not
#             redistributed here.
#   pylgm   — PyPI metadata and the sdist of the latest stable release (MIT).
# Usage: bash AI-internal/data-acquisition/fetch_python_inla_candidates.sh   (from repo root)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
DEST="$ROOT/Archive/python-inla-candidates"
LOG="$ROOT/AI-internal/data-acquisition/fetch_python_inla_candidates.log"
: > "$LOG"
if [ -e "$DEST" ]; then echo "exists, refusing to overwrite: $DEST" | tee -a "$LOG"; exit 1; fi
mkdir -p "$DEST/pyinla" "$DEST/pylgm"
date -u +%Y-%m-%dT%H:%M:%SZ | tee -a "$LOG"
for p in pyinla pylgm; do
  curl -fsSL "https://pypi.org/pypi/$p/json" -o "$DEST/$p/pypi.json"
  echo "$p $(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["info"]["version"])' "$DEST/$p/pypi.json")" | tee -a "$LOG"
done
url=$(python3 -c 'import json,sys; print([f["url"] for f in json.load(open(sys.argv[1]))["urls"] if f["packagetype"]=="sdist"][0])' "$DEST/pylgm/pypi.json")
curl -fsSL "$url" -o "$DEST/pylgm/$(basename "$url")"
tar -xzf "$DEST/pylgm/$(basename "$url")" -C "$DEST/pylgm"
echo "pylgm sdist $url $(shasum -a 256 "$DEST/pylgm/$(basename "$url")" | cut -c1-64)" | tee -a "$LOG"
(cd "$DEST" && find . -type f ! -name sha256sums.txt -print0 | LC_ALL=C sort -z | xargs -0 shasum -a 256) > "$DEST/sha256sums.txt"
