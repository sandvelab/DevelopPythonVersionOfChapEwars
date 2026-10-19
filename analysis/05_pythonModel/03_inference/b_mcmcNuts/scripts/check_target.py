"""Is the density NUTS samples the density candidate (a) approximates?

For every development dataset x config variant, at 20 random points (theta, x), the NumPyro
log density (mapped from the sampled coordinates to (theta, z) with its Jacobian) is set
beside the joint log density written with ewars_python's own pieces:
    log p(theta) + 1/2 prior_logdet_z(theta) - 1/2 z' Q(theta) z + sum log p(y | eta).
The two may differ by a constant; the spread of the difference across points is the check.
Both parametrisations of mcmc_nuts.Target are checked.
The points are drawn from a fixed generator (seed below), not from the posterior.

Usage: check_target.py <harness results> <configs dir> <package dir> <out tsv>
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

harness, configs, package, out = (Path(a) for a in sys.argv[1:5])
sys.path.insert(0, str(package))
sys.path.insert(0, str(Path(__file__).parent))
import jax.numpy as jnp  # noqa: E402
from numpyro.infer.util import log_density  # noqa: E402

import mcmc_nuts  # noqa: E402  (sets up JAX before its first use)
from ewars_python.frame import build_frame, parse_config  # noqa: E402
from ewars_python.latent import RW1_DIAGONAL, build_latent  # noqa: E402
from ewars_python.laplace import log_prior_theta  # noqa: E402
from ewars_python.primitives import nb_loglik  # noqa: E402

SEED = 20261018  # draws test points only; no result depends on its value
rng = np.random.default_rng(SEED)
rows = []
for ds in ["monthly_ewars", "weekly_nicaragua"]:
    for var in ["default", "nlags_3_6", "no_covariates", "region_seasonal"]:
        cfg = parse_config(configs / f"{var}.yml")
        mf = build_frame(harness / "inputs" / ds / "historic.csv", harness / "inputs" / ds / "future.csv", cfg)
        lat = build_latent(mf, cfg["precision"])
        for par in ["split", "centred"]:
            t = mcmc_nuts.Target(lat, parametrisation=par)
            diffs = []
            for _ in range(20):
                th = np.concatenate([[rng.uniform(-1, 4)], rng.uniform(-2, 8, lat.n_theta - 1)])
                s = {"theta": th, "r_s": rng.normal(0, 1, t.m)}
                # log density in z = in the sampled coordinates - log |d z / d sampled|
                jac = 0.5 * np.sum(np.log(np.exp(th[2]) * t.lam + RW1_DIAGONAL))
                if par == "split":
                    s.update(r_bar=rng.normal(), w=rng.normal(0, 1, t.n_u - 1), a=rng.normal(0, 3))
                    if lat.p_fixed > 1:
                        s["r_f"] = rng.normal(0, 0.05, lat.p_fixed - 1)
                    jac += 0.5 * th[1] - np.sum(np.log(t.fixed_sd[1:]))
                else:
                    s.update(u=rng.normal(0, 1, t.n_u), r_f=rng.normal(0, 0.05, lat.p_fixed))
                    jac += -np.sum(np.log(t.fixed_sd))
                if lat.region_seasonal:
                    s["r_s2"] = rng.normal(0, 1, (lat.n_spat, t.m))
                ld, _ = log_density(t.model, (), {}, {k: jnp.asarray(v) for k, v in s.items()})
                if lat.region_seasonal:
                    jac += 0.5 * lat.n_spat * np.sum(np.log(np.exp(th[3]) * t.lam + RW1_DIAGONAL))
                x = t.latent_draws({k: np.asarray(v)[None] for k, v in s.items()})[0]
                z = lat.T.T @ x
                eta = (lat.A @ x + lat.offset)[lat.obs]
                ref = (log_prior_theta(th) + 0.5 * lat.prior_logdet_z(th) - 0.5 * z @ lat.prior_precision_z(th) @ z
                       + np.sum(nb_loglik(lat.y[lat.obs], eta, np.exp(th[0]))))
                diffs.append(float(ld) + jac - ref)
                roundtrip = float(np.max(np.abs(lat.T @ z - x)))
            diffs = np.array(diffs)
            rows.append({"dataset": ds, "variant": var, "parametrisation": par, "points": len(diffs),
                         "difference_median": np.median(diffs), "difference_spread": diffs.max() - diffs.min(),
                         "x_Tz_roundtrip": roundtrip})
            print(rows[-1], flush=True)
pd.DataFrame(rows).to_csv(out, sep="\t", index=False)
