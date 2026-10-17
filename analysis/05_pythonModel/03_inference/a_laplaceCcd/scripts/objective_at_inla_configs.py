"""The Python Laplace log posterior evaluated at INLA's own integration points (configs.csv of
every clean R sweep fit), against the relative log posterior INLA recorded there.

Isolates the objective (priors, scaling, constraints, likelihood, Gaussian approximation)
from the search for the mode and the design: both are evaluated at the same theta.

Usage: objective_at_inla_configs.py <harness results> <configs dir> <package dir> <out tsv>
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

harness, configs, package, out = (Path(a) for a in sys.argv[1:5])
sys.path.insert(0, str(package))
from ewars_python.frame import build_frame, parse_config  # noqa: E402
from ewars_python.latent import build_latent  # noqa: E402
from ewars_python.laplace import LaplaceModel  # noqa: E402

rows = []
for ds in ["monthly_ewars", "weekly_nicaragua"]:
    for var in ["default", "nlags_3_6", "no_covariates", "region_seasonal"]:
        cfg = parse_config(configs / f"{var}.yml")
        mf = build_frame(harness / "inputs" / ds / "historic.csv", harness / "inputs" / ds / "future.csv", cfg)
        model = LaplaceModel(build_latent(mf, cfg["precision"]))
        for rep in sorted((harness / "fits" / ds / var).iterdir()):
            c = pd.read_csv(rep / "configs.csv")
            th = c[[k for k in c.columns if k.startswith("theta_")]].to_numpy()
            lp = np.array([model.log_post(t) for t in th])
            i0 = int(np.argmax(c["log_posterior_orig"].to_numpy()))
            for k in range(len(c)):
                rows.append({"dataset": ds, "variant": var, "r_run": rep.name, "config": k + 1,
                             "inla_rel_log_post": c["log_posterior_orig"].iloc[k],
                             "python_rel_log_post": lp[k] - lp[i0],
                             "diff": (lp[k] - lp[i0]) - c["log_posterior_orig"].iloc[k]})
df = pd.DataFrame(rows)
df.to_csv(out, sep="\t", index=False)
print(df.assign(absd=df["diff"].abs()).groupby(["dataset", "variant", "r_run"])["absd"].max().to_string())
