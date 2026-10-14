#!/usr/bin/env bash
# Clone the external repositories this project is anchored to into Archive/<name>/src,
# record the commit each was at, drop .git (the commit is the pin), and write a checksum
# manifest. Re-running with PIN_<NAME>=<sha> set re-obtains exactly the archived state.
# Usage: bash AI-internal/data-acquisition/fetch_repos.sh   (from the repository root)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
LOG="$ROOT/AI-internal/data-acquisition/fetch_repos.log"
: > "$LOG"
fetch() {  # name url pin-env-var
  local name="$1" url="$2" pin="${!3:-}"
  local dest="$ROOT/Archive/$name/src"
  if [ -d "$dest" ]; then echo "exists, skipping: $dest" | tee -a "$LOG"; return; fi
  mkdir -p "$ROOT/Archive/$name"
  local tmp; tmp="$(mktemp -d)"
  git clone --quiet "$url" "$tmp/repo" 2>&1 | tee -a "$LOG"
  if [ -n "$pin" ]; then git -C "$tmp/repo" checkout --quiet "$pin"; fi
  local sha date
  sha="$(git -C "$tmp/repo" rev-parse HEAD)"
  date="$(git -C "$tmp/repo" log -1 --format=%cI)"
  rm -rf "$tmp/repo/.git"
  mv "$tmp/repo" "$dest"
  (cd "$dest" && find . -type f -print0 | LC_ALL=C sort -z | xargs -0 shasum -a 256) > "$ROOT/Archive/$name/sha256sums.txt"
  echo "$name $url $sha $date $(du -sk "$dest" | cut -f1)KB" | tee -a "$LOG"
}
fetch chapkit_ewars_model https://github.com/chap-models/chapkit_ewars_model.git PIN_EWARS
fetch chap-core           https://github.com/dhis2-chap/chap-core.git           PIN_CHAPCORE
fetch chapkit             https://github.com/dhis2-chap/chapkit.git             PIN_CHAPKIT
fetch dlnmpy              https://github.com/Logic06183/dlnmpy.git              PIN_DLNMPY
