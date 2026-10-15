#!/usr/bin/env bash
# CH-20 diagnostic: the default config fitted 3 times per dataset with INLA single-threaded,
# all with replicate 1's seeds, so that any difference between the three is not a seed.
#
# Usage: run_thread_diagnostic.sh <inputs_dir> <seeds_tsv> <out_dir>
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
IN="$(cd "$1" && pwd)"; SEEDS="$2"; OUT="$(mkdir -p "$3" && cd "$3" && pwd)"
IMG=ghcr.io/chap-models/chapkit_ewars_model@sha256:959fb4f0f1b9d257a9697925f4500fd8ec4ffa9e1bb3ed7fc36e4f5c57c6ff88
read -r RS IS < <(awk -F'\t' '$1=="rep1"{print $3, $5}' "$SEEDS")
printf 'dataset\tvariant\treplicate\tseconds\texit_code\n' > "$OUT/timings.tsv"
for ds in monthly_ewars weekly_nicaragua; do
  for k in 1 2 3; do
    d="$OUT/$ds/default/single_thread_run$k"; rm -rf "$d"; mkdir -p "$d"; start=$SECONDS; rc=0
    docker run --rm --platform linux/amd64 --user root --entrypoint Rscript \
      -v "$SCRIPT_DIR:/s:ro" -v "$REPO_ROOT/Archive/chapkit_ewars_model/src/scripts:/src:ro" \
      -v "$IN:/in:ro" -v "$d:/out" "$IMG" \
      /s/instrument_single_thread.R /src "/in/$ds/historic.csv" "/in/$ds/future.csv" \
      /s/configs/default.yml /out "$RS" "$IS" < /dev/null > "$d/run.log" 2>&1 || rc=$?
    [ -f "$d/predictions.csv" ] && gzip -n -f "$d/predictions.csv"
    printf '%s\tdefault\tsingle_thread_run%s\t%s\t%s\n' "$ds" "$k" "$((SECONDS - start))" "$rc" >> "$OUT/timings.tsv"
    echo "$ds single_thread_run$k rc=$rc $((SECONDS - start))s"
  done
done
