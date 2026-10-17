"""L5: the Python model's chap evaluations against the R original's and chap's baselines,
with 04_fidelityMetrics' measures. Every R evaluation is kept (the crashed monthly one is
counted in 04's l5_evaluations.tsv).

Usage: compare_l5.py <python l5 rows dir> <R l5 rows dir> <fidelity scripts dir> <out dir>
"""

import itertools
import sys
from pathlib import Path

import pandas as pd

pydir, rdir, fid, out = (Path(a) for a in sys.argv[1:5])
sys.path.insert(0, str(fid))
from fidelity import compare_chap_rows  # noqa: E402


def load(d):
    return {tuple(f.stem.split("__")): pd.read_csv(f, sep="\t") for f in sorted(d.glob("*.tsv"))}


P, R = load(pydir), load(rdir)
rows, agg = [], []
for k, v in {**P, **R}.items():
    agg.append({"dataset": k[0], "model": k[1], "run": k[2], "n_rows": len(v), "mean_crps": v["crps"].mean()})
for ds in sorted({k[0] for k in P}):
    py = sorted(k for k in P if k[0] == ds)
    r = sorted(k for k in R if k[0] == ds and k[1] == "ewars_r")
    base = sorted(k for k in R if k[0] == ds and k[1] not in ("ewars_r",))
    for a in r:
        for b in py:
            rows.append({"dataset": ds, "comparison": "python_vs_r", "run_a": a[2], "run_b": b[2], **compare_chap_rows(R[a], P[b])})
    for a, b in itertools.combinations(py, 2):
        rows.append({"dataset": ds, "comparison": "python_vs_python", "run_a": a[2], "run_b": b[2], **compare_chap_rows(P[a], P[b])})
    for a, b in itertools.combinations(r, 2):
        rows.append({"dataset": ds, "comparison": "r_vs_r", "run_a": a[2], "run_b": b[2], **compare_chap_rows(R[a], R[b])})
    for b in py:
        for bl in base:
            rows.append({"dataset": ds, "comparison": f"python_vs_{bl[1]}", "run_a": b[2], "run_b": bl[1], **compare_chap_rows(P[b], R[bl])})
out.mkdir(parents=True, exist_ok=True)
pd.DataFrame(rows).to_csv(out / "l5_pairs.tsv", sep="\t", index=False)
pd.DataFrame(agg).sort_values(["dataset", "model", "run"]).to_csv(out / "l5_evaluations.tsv", sep="\t", index=False)
d = pd.DataFrame(rows)
print(pd.DataFrame(agg).sort_values(["dataset", "model", "run"]).to_string())
print(d.groupby(["dataset", "comparison"])[["mean_diff", "median_abs_diff", "mean_abs_diff"]].median().round(3).to_string())
