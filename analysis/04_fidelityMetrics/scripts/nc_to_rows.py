"""L5 rows: one chap evaluation file (.nc) as a table of forecast rows.

Runs under chap-core's own environment (claim.md, Environment), because reading chap's
netCDF output needs xarray and a netCDF backend, which the main environment does not carry.

One row per (location, time_period, horizon_distance) that has an observation: the observed
value, the forecast mean and quantiles, and the sample CRPS (fidelity.sample_crps).

Usage: nc_to_rows.py <evaluation.nc> <out.tsv>
"""

import sys

import numpy as np
import pandas as pd
import xarray as xr

from fidelity import QUANTILES, sample_crps

nc, out = sys.argv[1], sys.argv[2]
ds = xr.open_dataset(nc)
fc = ds["forecast"].transpose("location", "time_period", "horizon_distance", "sample")
obs = ds["observed"]
rows = []
for li, loc in enumerate(fc["location"].values):
    for ti, tp in enumerate(fc["time_period"].values):
        y = float(obs.sel(location=loc, time_period=tp))
        for hi, h in enumerate(fc["horizon_distance"].values):
            s = fc.values[li, ti, hi, :]
            if np.isnan(s).all() or np.isnan(y):
                continue
            rows.append((str(loc), str(tp), int(h), y, s))
S = np.array([r[4] for r in rows], dtype=float)
Y = np.array([r[3] for r in rows])
q = np.quantile(S, QUANTILES, axis=1)
table = pd.DataFrame({
    "location": [r[0] for r in rows], "time_period": [r[1] for r in rows],
    "horizon_distance": [r[2] for r in rows], "observed": Y, "mean": S.mean(axis=1),
    **{f"q{int(p * 100):02d}": q[i] for i, p in enumerate(QUANTILES)},
    "crps": sample_crps(S, Y),
})
table.to_csv(out, sep="\t", index=False)
print(f"{nc}: {len(table)} rows, mean crps {table['crps'].mean():.6g}")
