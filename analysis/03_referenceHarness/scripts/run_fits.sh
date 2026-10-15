#!/usr/bin/env bash
# The instrumented R reference over every development dataset x config variant x seeded
# replicate, one container per fit, in sequence (so each fit's timing is its own), plus one
# repeat of replicate 1 per dataset under the default config to test that a seeded run
# reproduces exactly.
#
# Usage: run_fits.sh <inputs_dir> <seeds_tsv> <out_dir>
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
IN="$(cd "$1" && pwd)"; SEEDS="$2"; OUT="$(mkdir -p "$3" && cd "$3" && pwd)"
IMG=ghcr.io/chap-models/chapkit_ewars_model@sha256:959fb4f0f1b9d257a9697925f4500fd8ec4ffa9e1bb3ed7fc36e4f5c57c6ff88
DATASETS=(monthly_ewars weekly_nicaragua)
VARIANTS=(default region_seasonal nlags_3_6 no_covariates)

TIMINGS="$OUT/timings.tsv"
printf 'dataset\tvariant\treplicate\tseconds\texit_code\n' > "$TIMINGS"

fit() {  # fit <dataset> <variant> <run_label> <r_seed> <inla_seed>
  local ds="$1" v="$2" label="$3" rs="$4" is="$5" start=$SECONDS rc=0
  local d="$OUT/$ds/$v/$label"
  rm -rf "$d"; mkdir -p "$d"
  docker run --rm --platform linux/amd64 --user root --entrypoint Rscript \
    -v "$SCRIPT_DIR:/s:ro" -v "$REPO_ROOT/Archive/chapkit_ewars_model/src/scripts:/src:ro" \
    -v "$IN:/in:ro" -v "$d:/out" "$IMG" \
    /s/instrument_reference.R /src "/in/$ds/historic.csv" "/in/$ds/future.csv" \
    "/s/configs/$v.yml" /out "$rs" "$is" < /dev/null > "$d/run.log" 2>&1 || rc=$?
  [ -f "$d/predictions.csv" ] && gzip -n -f "$d/predictions.csv"
  printf '%s\t%s\t%s\t%s\t%s\n' "$ds" "$v" "$label" "$((SECONDS - start))" "$rc" >> "$TIMINGS"
  echo "$ds $v $label rc=$rc $((SECONDS - start))s"
}

while IFS=$'\t' read -r rep _ rs _ is; do
  [ "$rep" = replicate ] && continue
  for ds in "${DATASETS[@]}"; do
    for v in "${VARIANTS[@]}"; do
      fit "$ds" "$v" "$rep" "$rs" "$is"
    done
  done
  if [ "$rep" = rep1 ]; then
    for ds in "${DATASETS[@]}"; do fit "$ds" default rep1_repeat "$rs" "$is"; done
  fi
done < "$SEEDS"
