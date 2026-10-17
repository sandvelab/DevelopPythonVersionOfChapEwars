"""Python (candidate a) against the R reference at L3 and L4, with 04_fidelityMetrics'
measures: every Python replicate against every R run of the same dataset x variant, each
pair labelled by the R run's health (every R run kept, plan §4b 2026-10-17); also the
Python replicates among themselves (sampler seed only).

Usage: compare_with_r.py <python fits dir> <harness results> <fidelity scripts dir> <r health tsv> <out dir>
"""

import itertools
import sys
from pathlib import Path

import pandas as pd

py, harness, fid, health_tsv, out = (Path(a) for a in sys.argv[1:6])
sys.path.insert(0, str(fid))
from fidelity import (compare_posterior, compare_predictive, read_posterior, read_samples,  # noqa: E402
                      summarise_posterior, summarise_predictive)

health = pd.read_csv(health_tsv, sep="\t")
health = health[health["run_set"] == "fits"].set_index(["dataset", "variant", "replicate"])["health"]
l3, l4, l3d, l4d = [], [], [], []
for dsdir in sorted(py.iterdir()):
    ds = dsdir.name
    fut = set(pd.read_csv(harness / "inputs" / ds / "future.csv")["time_period"].astype(str))
    for vdir in sorted(dsdir.iterdir()):
        var = vdir.name
        py_runs = sorted(p.name for p in vdir.iterdir())
        r_runs = sorted(p.name for p in (harness / "fits" / ds / var).iterdir())
        P = {r: (read_posterior(vdir / r), read_samples(vdir / r)) for r in py_runs}
        R = {r: (read_posterior(harness / "fits" / ds / var / r), read_samples(harness / "fits" / ds / var / r))
             for r in r_runs}
        pairs = [("python_vs_r", a, b, health[(ds, var, b)], P[a], R[b]) for a in py_runs for b in r_runs]
        pairs += [("python_vs_python", a, b, "-", P[a], P[b]) for a, b in itertools.combinations(py_runs, 2)]
        for kind, a, b, h, A, B in pairs:
            meta = {"dataset": ds, "variant": var, "comparison": kind, "run_a": a, "run_b": b, "r_health": h}
            m3 = compare_posterior(B[0], A[0]) if kind == "python_vs_r" else compare_posterior(A[0], B[0])
            l3d.append(m3.assign(**meta))
            l3 += [{**meta, **s} for s in summarise_posterior(m3).to_dict("records")]
            m4 = compare_predictive(B[1], A[1]) if kind == "python_vs_r" else compare_predictive(A[1], B[1])
            l4d.append(m4.assign(**meta))
            l4 += [{**meta, **s} for s in summarise_predictive(m4, fut).to_dict("records")]
out.mkdir(parents=True, exist_ok=True)
pd.DataFrame(l3).to_csv(out / "l3_python_vs_r_pairs.tsv", sep="\t", index=False)
pd.DataFrame(l4).to_csv(out / "l4_python_vs_r_pairs.tsv", sep="\t", index=False)
pd.concat(l3d).to_csv(out / "l3_python_vs_r_quantities.tsv.gz", sep="\t", index=False)
pd.concat(l4d).to_csv(out / "l4_python_vs_r_rows.tsv.gz", sep="\t", index=False)
d3 = pd.DataFrame(l3)
print(d3.groupby(["dataset", "variant", "comparison", "r_health", "group"])[["median_abs_z", "max_abs_z"]]
      .median().round(3).to_string())
