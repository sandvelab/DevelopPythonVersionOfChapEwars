#!/usr/bin/env bash
# Archive the R sources the Python port needs as design and test oracle (plan §4,
# "Modelling resources"; batch 3), at the versions found inside the R reference image:
#   Archive/r-sources/r-inla/      hrue/r-inla at tag Version_<installed INLA version>:
#                                  rinla/R/, inlaprog/src/, gmrflib/rw.{c,h}, and the .tex
#                                  documentation of latent models, likelihoods, priors, hyper
#   Archive/r-sources/dlnm/        the CRAN source tarball of the installed dlnm version
#   Archive/r-sources/reference-image/  dump_reference_image.R run inside the image
# Usage: bash AI-internal/data-acquisition/fetch_r_sources.sh   (from the repository root)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
HERE="$ROOT/AI-internal/data-acquisition"
DEST="$ROOT/Archive/r-sources"
LOG="$HERE/fetch_r_sources.log"
IMG=ghcr.io/chap-models/chapkit_ewars_model@sha256:959fb4f0f1b9d257a9697925f4500fd8ec4ffa9e1bb3ed7fc36e4f5c57c6ff88
: > "$LOG"
if [ -e "$DEST" ]; then echo "exists, refusing to overwrite: $DEST" | tee -a "$LOG"; exit 1; fi
mkdir -p "$DEST/reference-image" "$DEST/r-inla" "$DEST/dlnm"
manifest() { (cd "$1" && find . -type f ! -name sha256sums.txt -print0 | LC_ALL=C sort -z | xargs -0 shasum -a 256) > "$1/sha256sums.txt"; }

# 1. What the image runs.
docker run --rm --platform linux/amd64 --user root --entrypoint Rscript \
  -v "$HERE/dump_reference_image.R:/dump.R:ro" -v "$DEST/reference-image:/out" "$IMG" /dump.R 2>&1 | tee -a "$LOG"
INLA_VER=$(awk -F'\t' '$1=="INLA"{print $2}' "$DEST/reference-image/package_versions.tsv")
DLNM_VER=$(awk -F'\t' '$1=="dlnm"{print $2}' "$DEST/reference-image/package_versions.tsv")
echo "installed INLA $INLA_VER, dlnm $DLNM_VER" | tee -a "$LOG"
manifest "$DEST/reference-image"

# 2. r-inla at the tag of the installed version (partial clone; only the needed paths copied).
tmp="$(mktemp -d)"
git clone --quiet --filter=blob:none --no-checkout https://github.com/hrue/r-inla.git "$tmp/r-inla"
git -C "$tmp/r-inla" checkout --quiet "Version_$INLA_VER"
sha="$(git -C "$tmp/r-inla" rev-parse HEAD)"
(cd "$tmp/r-inla" && git ls-files \
 | grep -E '^(rinla/R/|inlaprog/src/|gmrflib/rw\.[ch]$|r-inla\.org/doc/(latent|likelihood|prior|hyper)/.*\.tex$|LICENSE|COPYING)' \
 | while read -r f; do mkdir -p "$DEST/r-inla/src/$(dirname "$f")"; cp "$f" "$DEST/r-inla/src/$f"; done)
echo "r-inla https://github.com/hrue/r-inla.git tag Version_$INLA_VER commit $sha $(du -sk "$DEST/r-inla/src" | cut -f1)KB" | tee -a "$LOG"
echo "$sha" > "$DEST/r-inla/commit.txt"
rm -rf "$tmp"
manifest "$DEST/r-inla"

# 3. dlnm from CRAN: the current contrib URL, falling back to the archive.
url="https://cran.r-project.org/src/contrib/dlnm_${DLNM_VER}.tar.gz"
curl -fsSL -o "$DEST/dlnm/dlnm_${DLNM_VER}.tar.gz" "$url" \
  || { url="https://cran.r-project.org/src/contrib/Archive/dlnm/dlnm_${DLNM_VER}.tar.gz";
       curl -fsSL -o "$DEST/dlnm/dlnm_${DLNM_VER}.tar.gz" "$url"; }
tar -xzf "$DEST/dlnm/dlnm_${DLNM_VER}.tar.gz" -C "$DEST/dlnm"
echo "dlnm $url $(shasum -a 256 "$DEST/dlnm/dlnm_${DLNM_VER}.tar.gz" | cut -c1-64)" | tee -a "$LOG"
manifest "$DEST/dlnm"
du -sh "$DEST"/* | tee -a "$LOG"
