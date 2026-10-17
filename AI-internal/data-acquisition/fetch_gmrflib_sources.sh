#!/usr/bin/env bash
# Archive GMRFLib, the C library that carries INLA's approximation engine, at the same r-inla
# tag as Archive/r-sources/ (batch 8, inference candidate a). fetch_r_sources.sh archived only
# gmrflib/rw.{c,h}; the integration design (CCD), the hyperparameter mode search, the
# skewness-corrected standard deviations, the VB correction and the posterior sampler live in
# the rest of gmrflib/, which candidate (a) follows as its specification.
#   Archive/r-inla-gmrflib/src/gmrflib/   every *.c and *.h under gmrflib/ at the tag
# Usage: bash AI-internal/data-acquisition/fetch_gmrflib_sources.sh   (from the repository root)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
HERE="$ROOT/AI-internal/data-acquisition"
DEST="$ROOT/Archive/r-inla-gmrflib"
LOG="$HERE/fetch_gmrflib_sources.log"
SHA_EXPECTED="$(cat "$ROOT/Archive/r-sources/r-inla/commit.txt")"
: > "$LOG"
if [ -e "$DEST" ]; then echo "exists, refusing to overwrite: $DEST" | tee -a "$LOG"; exit 1; fi
mkdir -p "$DEST/src"
tmp="$(mktemp -d)"
git clone --quiet --filter=blob:none --no-checkout https://github.com/hrue/r-inla.git "$tmp/r-inla"
git -C "$tmp/r-inla" checkout --quiet "$SHA_EXPECTED"
sha="$(git -C "$tmp/r-inla" rev-parse HEAD)"
[ "$sha" = "$SHA_EXPECTED" ] || { echo "commit mismatch: $sha" | tee -a "$LOG"; exit 1; }
(cd "$tmp/r-inla" && git ls-files \
 | grep -E '^(gmrflib/.*\.[ch]$|LICENSE|COPYING)' \
 | while read -r f; do mkdir -p "$DEST/src/$(dirname "$f")"; cp "$f" "$DEST/src/$f"; done)
echo "$sha" > "$DEST/commit.txt"
echo "r-inla https://github.com/hrue/r-inla.git commit $sha gmrflib $(find "$DEST/src/gmrflib" -type f | wc -l | tr -d ' ') files $(du -sk "$DEST/src" | cut -f1)KB" | tee -a "$LOG"
rm -rf "$tmp"
(cd "$DEST" && find . -type f ! -name sha256sums.txt -print0 | LC_ALL=C sort -z | xargs -0 shasum -a 256) > "$DEST/sha256sums.txt"
