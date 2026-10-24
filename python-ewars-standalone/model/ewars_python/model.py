"""predict.R predict_chap, end to end: frame, fit, predictive samples, output file."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from . import inla_approx
from .frame import build_frame, parse_config
from .latent import build_latent

N_SAMPLES = 1000  # predict.R: s <- 1000
PROJECT_SEED = 20261014


def derive_seed(*parts: bytes) -> int:
    """A seed valid for numpy, from the project seed and the given byte strings: the
    project's component-seed rule (readme-at-start.md), applied to the component
    "20261014/python-predict/<sha256 of the inputs>"."""
    h = hashlib.sha256()
    for p in parts:
        h.update(hashlib.sha256(p).digest())
    component = f"{PROJECT_SEED}/python-predict/{h.hexdigest()}"
    return 1 + int.from_bytes(hashlib.sha256(component.encode()).digest()[:4], "big") % (2 ** 31 - 2)


def predict_chap(hist_fn, future_fn, preds_fn, config_path, seed: int | None = None,
                 diagnostics_dir=None, n_samples: int = N_SAMPLES) -> pd.DataFrame:
    config = parse_config(config_path)
    print(f"Config: n_lags={','.join(map(str, config['n_lags']))} precision={config['precision']} "
          f"region_seasonal={config['region_seasonal']}")
    print(f"Covariates: {', '.join(config['additional_continuous_covariates'])}")
    if seed is None:
        seed = derive_seed(Path(hist_fn).read_bytes(), Path(future_fn).read_bytes(),
                           json.dumps(config, sort_keys=True).encode())
    mf = build_frame(hist_fn, future_fn, config)
    lat = build_latent(mf, config["precision"])
    fit = inla_approx.fit(lat)
    rng = np.random.default_rng(seed)
    size, eta = inla_approx.sample_predictor(fit, n_samples, rng, rows=mf.pred_idx)
    # rnbinom(mu = exp(Predictor), size = theta[1]) per sample; numpy's negative_binomial
    # takes (n, p) with p = size / (size + mu), the same distribution (CH-15)
    mu = np.exp(eta)
    p = size[None, :] / (size[None, :] + mu)
    y_pred = rng.negative_binomial(np.broadcast_to(size[None, :], mu.shape), p)
    out = pd.DataFrame(y_pred, columns=[f"sample_{i}" for i in range(n_samples)])
    out.insert(0, "location", mf.df["location"].to_numpy()[mf.pred_idx])
    out.insert(0, "time_period", mf.df["time_period"].to_numpy()[mf.pred_idx])
    out.to_csv(preds_fn, index=False)
    if diagnostics_dir is not None:
        inla_approx.write_summaries(fit, mf, Path(diagnostics_dir), seed=seed)
        out.to_csv(Path(diagnostics_dir) / "predictions.csv.gz", index=False)
    return out
