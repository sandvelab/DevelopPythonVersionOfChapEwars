"""Candidate (b) at L3 and L4, with 04_fidelityMetrics' measures, against:
  - every R run of the same dataset x variant, each pair labelled by the R run's health
    (every R run kept, plan §4b 2026-10-17): comparison "mcmc_vs_r";
  - itself, replicate against replicate (the MCMC's own Monte Carlo floor): "mcmc_vs_mcmc";
  - candidate (a)'s fits, read from that node's committed results: "mcmc_vs_laplace".
Shifts are signed as (b - other) / pooled sd.

Usage: compare.py <mcmc fits dir> <laplace fits dir> <harness results> <fidelity scripts dir>
                  <r health tsv> <out dir>
"""

import itertools
import sys
from pathlib import Path

import pandas as pd

mc, la, harness, fid, health_tsv, out = (Path(a) for a in sys.argv[1:7])
sys.path.insert(0, str(fid))
from fidelity import (compare_posterior, compare_predictive, read_posterior, read_samples,  # noqa: E402
                      summarise_posterior, summarise_predictive)

health = pd.read_csv(health_tsv, sep="\t")
health = health[health["run_set"] == "fits"].set_index(["dataset", "variant", "replicate"])["health"]
l3, l4, l3d, l4d = [], [], [], []
for dsdir in sorted(mc.iterdir()):
    ds = dsdir.name
    fut = set(pd.read_csv(harness / "inputs" / ds / "future.csv")["time_period"].astype(str))
    for vdir in sorted(dsdir.iterdir()):
        var = vdir.name

        def load(base):
            return {r.name: (read_posterior(r), read_samples(r)) for r in sorted(base.iterdir())}

        M = load(vdir)
        R = load(harness / "fits" / ds / var)
        L = load(la / ds / var)
        # (kind, run_a, run_b, r_health, other, this): measures are compare(other, this)
        pairs = [("mcmc_vs_r", a, b, health[(ds, var, b)], R[b], M[a]) for a in M for b in R]
        pairs += [("mcmc_vs_mcmc", a, b, "-", M[a], M[b]) for a, b in itertools.combinations(M, 2)]
        pairs += [("mcmc_vs_laplace", a, b, "-", L[b], M[a]) for a in M for b in L]
        for kind, a, b, h, other, this in pairs:
            meta = {"dataset": ds, "variant": var, "comparison": kind, "run_a": a, "run_b": b, "r_health": h}
            m3 = compare_posterior(other[0], this[0])
            l3d.append(m3.assign(**meta))
            l3 += [{**meta, **s} for s in summarise_posterior(m3).to_dict("records")]
            m4 = compare_predictive(other[1], this[1])
            l4d.append(m4.assign(**meta))
            l4 += [{**meta, **s} for s in summarise_predictive(m4, fut).to_dict("records")]
out.mkdir(parents=True, exist_ok=True)
pd.DataFrame(l3).to_csv(out / "l3_mcmc_pairs.tsv", sep="\t", index=False)
pd.DataFrame(l4).to_csv(out / "l4_mcmc_pairs.tsv", sep="\t", index=False)
pd.concat(l3d).to_csv(out / "l3_mcmc_quantities.tsv.gz", sep="\t", index=False)
pd.concat(l4d).to_csv(out / "l4_mcmc_rows.tsv.gz", sep="\t", index=False)
d3 = pd.DataFrame(l3)
print(d3.groupby(["dataset", "variant", "comparison", "r_health", "group"])[["median_abs_z", "max_abs_z"]]
      .median().round(3).to_string())
