"""Collect chap's metrics for the reference run into one table, with each evaluation's time.

Reads <run_dir>/metrics/<dataset>_metrics.csv (written by `chap export-metrics`) and
<run_dir>/timings.tsv, and writes <run_dir>/reference_scores.tsv: one row per dataset and
model, with chap's CRPS (the primary metric), MAE, RMSE, the two interval coverages, and the
wall-clock seconds. Values are copied, not recomputed.

Usage: summarise_reference.py <run_dir>
"""

import sys
from pathlib import Path

import pandas as pd

run = Path(sys.argv[1])
COLS = ["crps", "mae", "rmse", "coverage_10_90", "coverage_25_75"]
timings = pd.read_csv(run / "timings.tsv", sep="\t")
rows = []
for f in sorted((run / "metrics").glob("*_metrics.csv")):
    dataset = f.name.removesuffix("_metrics.csv")
    m = pd.read_csv(f)
    for _, r in m.iterrows():
        label = Path(r["filename"]).stem.split("__", 1)[1]
        t = timings[(timings["dataset"] == dataset) & (timings["model"] == label)]
        rows.append({"dataset": dataset, "model": label, "chap_model_name": r["model_name"],
                     **{c: r[c] for c in COLS},
                     "seconds": int(t["seconds"].iloc[0]) if len(t) else None})
out = pd.DataFrame(rows).sort_values(["dataset", "crps"])
out.to_csv(run / "reference_scores.tsv", sep="\t", index=False)
print(out.to_string(index=False))
