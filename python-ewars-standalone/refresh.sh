#!/usr/bin/env bash
# Rebuilds the copies in this folder from their sources in the analysis tree. Run from the
# repository root:  bash python-ewars-standalone/refresh.sh
# It replaces model/, data/, config/, LICENSE and NOTICE; it does not touch README.md,
# provenance.md, check/ or output/. After running it, append a section to provenance.md with the commit.
set -euo pipefail
cd "$(dirname "$0")/.."
HERE=python-ewars-standalone
SRC=analysis/05_pythonModel/scripts/chapkit_ewars_python

# The model, without anything a local run creates.
rm -rf "$HERE/model"
rsync -a --exclude .venv --exclude example_run --exclude data --exclude __pycache__ \
      --exclude '*.pyc' "$SRC/" "$HERE/model/"

# The two development datasets as chap reads them (one CSV each), and as the model reads
# them without chap (a historic and a future file each).
rm -rf "$HERE/data"
mkdir -p "$HERE/data"
cp analysis/01_referenceThroughChap/results/run1/inputs/weekly_nicaragua.csv "$HERE/data/"
cp analysis/01_referenceThroughChap/results/run1/inputs/monthly_ewars.csv "$HERE/data/"
for d in weekly_nicaragua monthly_ewars; do
  mkdir -p "$HERE/data/$d"
  cp analysis/03_referenceHarness/results/inputs/$d/historic.csv "$HERE/data/$d/"
  cp analysis/03_referenceHarness/results/inputs/$d/future.csv "$HERE/data/$d/"
done

# The model configuration: chap's form, and the flat form predict.py reads.
rm -rf "$HERE/config"
mkdir -p "$HERE/config"
cp analysis/01_referenceThroughChap/scripts/ewars_config.yaml "$HERE/config/"
cat > "$HERE/config/predict_config.yml" <<'EOF'
# The same settings as ewars_config.yaml, in the flat form scripts/predict.py reads when the
# model is run on two CSV files without chap.
n_lags: [3]
precision: 0.01
region_seasonal: false
additional_continuous_covariates: [rainfall, mean_temperature]
EOF

# The licence and the notice, so that a copy of this folder carries them.
cp LICENSE NOTICE "$HERE/"

echo "refreshed $HERE/model, data and config from $(git rev-parse --short HEAD)"
