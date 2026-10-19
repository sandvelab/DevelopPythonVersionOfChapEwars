"""Candidate (b) on the R harness's fit inputs: every development dataset x config variant,
n replicates each, a replicate being an independent NUTS run with its own seed. Writes per
run the files the instrumented R reference and candidate (a) write (fit_info.json,
hyperpar.csv, fixed.csv, random_*.csv, predictions.csv.gz), plus the hyperparameter draws
(theta_draws.csv.gz) and per-site convergence diagnostics (mcmc_diagnostics.csv).

Posterior summaries are means and sds over all draws (chains pooled). The 1000 predictive
samples per row take every (draws / 1000)-th draw and one rnbinom(mu, size) each, as
predict.R draws one per inla.posterior.sample.

Usage: run_mcmc_fits.py <harness results> <configs dir> <package dir> <out dir> <n_reps>
                        <num_warmup> <num_samples> <num_chains>
"""

import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

harness, configs, package, out = (Path(a) for a in sys.argv[1:5])
n_reps, num_warmup, num_samples, num_chains = (int(a) for a in sys.argv[5:9])
sys.path.insert(0, str(package))
sys.path.insert(0, str(Path(__file__).parent))
import mcmc_nuts  # noqa: E402  (sets up JAX before its first use)
from numpyro.diagnostics import summary  # noqa: E402

from ewars_python.frame import build_frame, parse_config  # noqa: E402
from ewars_python.inla_approx import HYPER_NAMES  # noqa: E402
from ewars_python.latent import build_latent  # noqa: E402
from ewars_python.model import N_SAMPLES, PROJECT_SEED  # noqa: E402


def component_seed(component: str) -> int:
    d = hashlib.sha256(f"{PROJECT_SEED}/{component}".encode()).digest()
    return 1 + int.from_bytes(d[:4], "big") % (2 ** 31 - 2)


def write_run(run: Path, mf, lat, t, mcmc, seed: int, seconds: float) -> None:
    grouped = mcmc.get_samples(group_by_chain=True)
    flat = {k: np.asarray(v).reshape((-1,) + v.shape[2:]) for k, v in grouped.items()}
    th = flat["theta"]
    n_draws = len(th)
    # hyperparameters on the natural scale, as INLA's summary.hyperpar reports them
    nat = np.exp(th)
    m = lat.n_theta
    pd.DataFrame({"name": HYPER_NAMES[:m], "mean": nat.mean(axis=0), "sd": nat.std(axis=0, ddof=1),
                  "0.025quant": np.quantile(nat, 0.025, axis=0), "0.5quant": np.quantile(nat, 0.5, axis=0),
                  "0.975quant": np.quantile(nat, 0.975, axis=0)}).to_csv(run / "hyperpar.csv", index=False)
    x = t.latent_draws(flat)
    mean, sd = x.mean(axis=0), x.std(axis=0, ddof=1)
    fb = lat.blocks["fixed"]
    pd.DataFrame({"name": mf.fixed_names, "mean": mean[fb], "sd": sd[fb]}).to_csv(run / "fixed.csv", index=False)
    terms = [("ID_spat", "u", lat.n_spat), ("ID_time_cyclic", "s", lat.n_cyc)]
    if lat.region_seasonal:
        terms.append(("ID_time_cyclic2", "s2", lat.n_cyc))
    for name, block, n in terms:  # the ID columns exactly as inla_approx.write_summaries writes them
        b = lat.blocks[block]
        ids = np.tile(np.arange(1, n + 1), (b.stop - b.start) // n)
        if block != "u":
            ids = np.tile(mf.cyc_values, (b.stop - b.start) // n)
        pd.DataFrame({"ID": ids, "mean": mean[b], "sd": sd[b]}).to_csv(run / f"random_{name}.csv", index=False)
    # predictive samples
    keep = np.arange(0, n_draws, n_draws // N_SAMPLES)[:N_SAMPLES]
    rng = np.random.default_rng(seed)
    eta = t.eta_rows(x[keep], mf.pred_idx)
    size = np.exp(th[keep, 0])
    mu = np.exp(eta)
    y_pred = rng.negative_binomial(np.broadcast_to(size[None, :], mu.shape), size[None, :] / (size[None, :] + mu))
    pred = pd.DataFrame(y_pred, columns=[f"sample_{i}" for i in range(N_SAMPLES)])
    pred.insert(0, "location", mf.df["location"].to_numpy()[mf.pred_idx])
    pred.insert(0, "time_period", mf.df["time_period"].to_numpy()[mf.pred_idx])
    pred.to_csv(run / "predictions.csv.gz", index=False)
    # draws and diagnostics
    chain = np.repeat(np.arange(1, num_chains + 1), num_samples)
    td = pd.DataFrame(th, columns=[f"theta_{i + 1}" for i in range(m)])
    td.insert(0, "draw", np.tile(np.arange(1, num_samples + 1), num_chains))
    td.insert(0, "chain", chain)
    td.to_csv(run / "theta_draws.csv.gz", index=False)
    sm = summary({k: np.asarray(v) for k, v in grouped.items()})
    diag = [{"site": k, "n": int(np.size(v["n_eff"])), "min_ess": float(np.min(v["n_eff"])),
             "median_ess": float(np.median(v["n_eff"])), "max_rhat": float(np.max(v["r_hat"]))} for k, v in sm.items()]
    pd.DataFrame(diag).to_csv(run / "mcmc_diagnostics.csv", index=False)
    ex = mcmc.get_extra_fields()
    steps = np.asarray(ex["num_steps"])
    info = {"engine": "numpyro NUTS (candidate b)", "seed": int(seed), "num_warmup": num_warmup,
            "num_samples": num_samples, "num_chains": num_chains, "n_theta": m,
            "divergences": int(np.asarray(ex["diverging"]).sum()),
            "mean_num_steps": float(steps.mean()), "max_tree_depth_hits": int((steps >= 1023).sum()),
            "min_ess": min(d["min_ess"] for d in diag), "max_rhat": max(d["max_rhat"] for d in diag),
            "theta_mean": [float(v) for v in th.mean(axis=0)], "seconds": round(seconds, 1)}
    (run / "fit_info.json").write_text(json.dumps(info, indent=2))


rows = []
for ds in ["monthly_ewars", "weekly_nicaragua"]:
    for var in ["default", "nlags_3_6", "no_covariates", "region_seasonal"]:
        cfg = parse_config(configs / f"{var}.yml")
        mf = build_frame(harness / "inputs" / ds / "historic.csv", harness / "inputs" / ds / "future.csv", cfg)
        lat = build_latent(mf, cfg["precision"])
        t = mcmc_nuts.Target(lat)
        for r in range(1, n_reps + 1):
            run = out / "fits" / ds / var / f"rep{r}"
            run.mkdir(parents=True, exist_ok=True)
            seed = component_seed(f"mcmc-fit/{ds}/{var}/rep{r}")
            t0 = time.time()
            mcmc = mcmc_nuts.run_nuts(t, seed, num_warmup, num_samples, num_chains)
            mcmc.get_samples()["theta"].block_until_ready()
            seconds = time.time() - t0
            write_run(run, mf, lat, t, mcmc, seed, seconds)
            info = json.loads((run / "fit_info.json").read_text())
            rows.append({"dataset": ds, "variant": var, "replicate": f"rep{r}", "seed": seed,
                         "seconds": info["seconds"], "divergences": info["divergences"],
                         "max_tree_depth_hits": info["max_tree_depth_hits"], "mean_num_steps": info["mean_num_steps"],
                         "min_ess": round(info["min_ess"], 1), "max_rhat": round(info["max_rhat"], 4)})
            print(rows[-1], flush=True)
pd.DataFrame(rows).to_csv(out / "mcmc_fits_summary.tsv", sep="\t", index=False)
