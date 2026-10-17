"""Inference candidate (a): INLA's compact-mode approximation, written in Python.

Followed step by step from INLA 25.10.19's sources (Archive/r-inla-gmrflib/, Archive/r-sources/;
section numbers refer to the batch 8 specification, analysis/05_pythonModel/03_inference/
a_laplaceCcd/results/inla_spec.md):

1. the hyperparameter mode theta* of the Laplace log posterior (laplace.py), from INLA's
   initial values, and the Hessian there by central differences with INLA's step
   sqrt(0.005), moving to a better point if the Hessian's evaluations find one (§5);
2. theta(z) = theta* + V Lambda^{-1/2} z, and skewness factors from z = +-sqrt(2) e_k,
   normalised so their product is 1 (§6);
3. the CCD design: centre, 2m axial and 2^m factorial points, at radius 1.1 sqrt(m), with
   INLA's integration weights; configurations below exp(-6.9) of the best are dropped (§7);
4. per configuration, the Gaussian approximation and INLA's VB correction of its mean (§9);
5. predictive draws: a configuration with probability proportional to its density times its
   weight, the latent field from the Gaussian approximation centred at the VB-corrected mean,
   under the constraints, and theta[1] = exp(theta_k[1]) (§10).

Engine settings that differ from INLA's are logged (JC-28): INLA's own BFGS and its
direction basis for differences are not ported; scipy's BFGS finds the mode, and the
Hessian is taken along the coordinate axes.
"""

from __future__ import annotations

import itertools
import json
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd
import scipy.linalg as sla
from scipy.optimize import minimize

from .latent import Latent
from .laplace import GaussApprox, LaplaceModel
from .primitives import nb_grad_hess

INITIAL_LOG_SIZE = 2.30258509299405  # inla.models()$likelihood$nbinomial$hyper$theta$initial
INITIAL_LOG_PREC = 4.0  # iid and rw1 initial
HESSIAN_STEP = np.sqrt(0.005)  # inlaprog/src/inla-parse.c:19095
F0 = 1.1  # gmrflib/approx-inference.c:65
LOG_DENS_DROP = np.log(1 - 0.999)  # configs below this relative density are not stored (§7)
VB_MAX_ITER = 25
VB_TOL = 0.01
VB_STEP_CAP = 5.001
VB_ABORT = 25.0
GH_N = 15


@dataclass
class Config:
    theta: np.ndarray
    log_post: float  # Laplace log posterior, unnormalised
    log_weight: float
    ga: GaussApprox
    mean_x: np.ndarray = None  # VB-corrected mean, full coordinates
    sd_x: np.ndarray = None  # Gaussian-approximation sd, full coordinates (constrained)
    vb_iter: int = 0
    vb_status: str = ""


@dataclass
class Fit:
    lat: Latent
    model: LaplaceModel
    theta_mode: np.ndarray
    hessian: np.ndarray
    V: np.ndarray
    lam: np.ndarray
    corr_pos: np.ndarray
    corr_neg: np.ndarray
    configs: list[Config]
    probs: np.ndarray  # sampling probabilities of the configs
    info: dict = field(default_factory=dict)


# ---------------------------------------------------------------- 1. mode and Hessian
def _mode(model: LaplaceModel, n_theta: int) -> tuple[np.ndarray, dict]:
    th0 = np.array([INITIAL_LOG_SIZE] + [INITIAL_LOG_PREC] * (n_theta - 1))
    neval = [0]

    def f(t):
        neval[0] += 1
        v = model.log_post(t)
        return -v if np.isfinite(v) else 1e12

    r = minimize(f, th0, method="BFGS", options={"gtol": 1e-5, "maxiter": 1000})
    return r.x, {"optimizer": "scipy BFGS", "optimizer_message": str(r.message), "optimizer_evals": neval[0]}


def _hessian(model: LaplaceModel, theta: np.ndarray, h: float) -> tuple[np.ndarray, np.ndarray, float]:
    """Central-difference Hessian of -log posterior (§5). Returns (H, best theta seen,
    its log posterior), so the caller can move the mode if a better point turns up."""
    m = len(theta)
    f0 = -model.log_post(theta)
    best_t, best_f = theta.copy(), f0
    H = np.zeros((m, m))
    E = np.eye(m) * h
    fp = np.zeros(m)
    fm = np.zeros(m)
    for i in range(m):
        fp[i] = -model.log_post(theta + E[i])
        fm[i] = -model.log_post(theta - E[i])
        for t, v in ((theta + E[i], fp[i]), (theta - E[i], fm[i])):
            if v < best_f:
                best_t, best_f = t.copy(), v
        H[i, i] = (fp[i] - 2 * f0 + fm[i]) / h ** 2
    for i, j in itertools.combinations(range(m), 2):
        fpp = -model.log_post(theta + E[i] + E[j])
        fmp = -model.log_post(theta - E[i] + E[j])
        fpm = -model.log_post(theta + E[i] - E[j])
        fmm = -model.log_post(theta - E[i] - E[j])
        H[i, j] = H[j, i] = (fpp - fmp - fpm + fmm) / (4 * h ** 2)
    return H, best_t, -best_f


# ---------------------------------------------------------------- 3. CCD design
def ccd_design(m: int) -> np.ndarray:
    """Centre, the 2m axial points and the full 2^m factorial, each non-centre point at unit
    norm (gmrflib/design.c, designP.h), for m = 3 (15 points) or 4 (25 points)."""
    pts = [np.zeros(m)]
    for k in range(m):
        for s in (1.0, -1.0):
            e = np.zeros(m)
            e[k] = s
            pts.append(e)
    for signs in itertools.product((1.0, -1.0), repeat=m):
        pts.append(np.array(signs) / np.sqrt(m))
    return np.array(pts)


def ccd_weights(m: int, n_points: int) -> tuple[float, float]:
    """INLA's CCD integration weights (gmrflib/approx-inference.c:2063-2087)."""
    f = max(F0, 1.0) * np.sqrt(m)
    w = 1.0 / ((n_points - 1) * (1.0 + np.exp(-f ** 2 / 2) * (f ** 2 / m - 1.0)))
    return w, 1.0 - (n_points - 1) * w


# ---------------------------------------------------------------- 4. VB mean correction
def _vb_set(lat: Latent) -> np.ndarray:
    """The latent nodes whose directions the VB correction uses (inlaprog/src/inla.c
    5842-5940): every fixed effect, and per f-term up to lim nodes per replicate."""
    terms = [("u", lat.n_spat, lat.n_year), ("s", lat.n_cyc, 1)]
    if lat.region_seasonal:
        terms.append(("s2", lat.n_cyc, lat.n_spat))
    nf = len(terms)
    idx = []
    for name, n, nrep in terms:
        start = lat.blocks[name].start
        lim = max(0, min(30, 1024 // (nf * nrep)))
        if n <= lim:
            sel = np.arange(n)
        elif lim == 0:
            sel = np.array([], dtype=int)
        else:
            ln = max(1, n // lim)
            k = max(1, ln // 2)
            sel = (np.arange(lim) * ln + k) % n
        for r in range(nrep):
            idx.extend(start + r * n + sel)
    idx.extend(range(lat.blocks["fixed"].start, lat.blocks["fixed"].stop))
    return np.array(sorted(set(int(i) for i in idx)))


def _row_index(lat: Latent):
    """Each row of A has the same number of non-zeros: its random-effect columns and every
    fixed-effect column. Returns (cols, vals), n_rows x k, for fast quadratic forms."""
    A = lat.A.tocsr()
    k = np.diff(A.indptr)
    kmax = int(k.max())
    cols = np.zeros((A.shape[0], kmax), dtype=int)
    vals = np.zeros((A.shape[0], kmax))
    for i in range(A.shape[0]):
        a, b = A.indptr[i], A.indptr[i + 1]
        cols[i, : b - a] = A.indices[a:b]
        vals[i, : b - a] = A.data[a:b]
    return cols, vals


def _vb_correct(lat: Latent, model: LaplaceModel, cfg: Config, Sx: np.ndarray, S: np.ndarray,
                rowcols, gh) -> None:
    """INLA's VB correction of the mean (§9; gmrflib/approx-inference.c:5168-5686)."""
    theta, ga = cfg.theta, cfg.ga
    size = np.exp(theta[0])
    mode = lat.T @ ga.z
    sd = np.sqrt(np.maximum(np.diag(Sx), 0))
    cols, vals = rowcols
    obs = lat.obs
    c_o, v_o = cols[obs], vals[obs]
    # predictor variances, fixed during the iterations
    var_eta = np.einsum("ij,ijk,ik->i", v_o, Sx[c_o[:, :, None], c_o[:, None, :]], v_o)
    M = Sx[:, S]
    Q0 = lat.prior_precision_x(theta)
    # Q_GA tabulated once: M' Q_GA M with Q_GA = Q0 + A' W A at the mode (Sigma_c Q Sigma_c)
    _, w = nb_grad_hess(model.y_obs, ga.eta[obs], size)
    QM = Q0 @ M + model.A_obs_T @ (model.A_obs @ M * w[:, None])
    MM = M.T @ QM
    U, sv, Vt = np.linalg.svd(MM)
    keep = sv > np.cbrt(np.finfo(float).eps) * sv.max()
    MM_pinv = (Vt[keep].T / sv[keep]) @ U[:, keep].T
    gx, gw = gh
    m = mode.copy()
    last, increases, status = np.inf, 0, "max_iter"
    for it in range(1, VB_MAX_ITER + 1):
        eta_bar = model.A_obs @ m + model.off_obs
        eta_q = eta_bar[:, None] + np.sqrt(var_eta)[:, None] * gx[None, :]
        g_q, _ = nb_grad_hess(model.y_obs[:, None], eta_q, size)
        BB = -(g_q @ gw)  # -E[l'(eta)]
        grad = Q0 @ m + model.A_obs_T @ BB
        delta = -MM_pinv @ (M.T @ grad)
        if not np.all(np.isfinite(delta)):
            status, m = "aborted_nan", mode.copy()
            break
        dm = M @ delta
        dm = np.clip(dm, -VB_STEP_CAP * sd, VB_STEP_CAP * sd)
        m = m + dm
        crit = float(np.max(np.abs(dm) / np.where(sd > 0, sd, 1)))
        if np.max(np.abs(m - mode) / np.where(sd > 0, sd, 1)) >= VB_ABORT:
            status, m = "aborted_far", mode.copy()
            break
        increases = increases + 1 if crit > last else 0
        if increases >= 3:
            status, m = "aborted_diverging", mode.copy()
            break
        last = crit
        if crit < VB_TOL:
            status = "converged"
            break
    cfg.mean_x, cfg.sd_x, cfg.vb_iter, cfg.vb_status = m, sd, it, status


# ---------------------------------------------------------------- the fit
def fit(lat: Latent) -> Fit:
    model = LaplaceModel(lat)
    m = lat.n_theta
    theta_mode, info = _mode(model, m)
    h = HESSIAN_STEP
    moves = 0
    while True:
        H, best_t, best_lp = _hessian(model, theta_mode, h)
        if best_lp > model.log_post(theta_mode) + 1e-10 and moves < 20:
            theta_mode, moves, h = best_t, moves + 1, h * 1.05  # "stupid search" (§5)
            continue
        break
    H = (H + H.T) / 2
    lam, V = np.linalg.eigh(H)
    if np.any(lam <= 0):  # INLA falls back to the diagonal (§5)
        lam, V = np.maximum(np.diag(H), 1e-8), np.eye(m)
    info.update({"hessian_moves": moves, "hessian_step": h})
    to_theta = V / np.sqrt(lam)  # theta(z) = theta* + to_theta @ z
    lp_mode = model.log_post(theta_mode)

    corr_pos, corr_neg = np.ones(m), np.ones(m)
    for k in range(m):
        for sgn, arr in ((1.0, corr_pos), (-1.0, corr_neg)):
            z = np.zeros(m)
            z[k] = sgn * np.sqrt(2.0)
            D = lp_mode - model.log_post(theta_mode + to_theta @ z)
            arr[k] = np.sqrt(1.0 / D) if D > 0 and np.isfinite(D) else 1.0
    g = np.sqrt(corr_pos * corr_neg)
    corr_pos, corr_neg = corr_pos / g, corr_neg / g

    design = ccd_design(m)
    w, w0 = ccd_weights(m, len(design))
    f = max(F0, 1.0) * np.sqrt(m)
    configs = []
    for i, d in enumerate(design):
        z = f * d * np.where(d > 0, corr_pos, corr_neg)
        th = theta_mode + to_theta @ z
        ga = model.approx(th)
        configs.append(Config(theta=th, log_post=ga.log_post, log_weight=np.log(w0 if i == 0 else w), ga=ga))
    lp = np.array([c.log_post for c in configs])
    keep = lp - lp.max() >= LOG_DENS_DROP
    configs = [c for c, k in zip(configs, keep) if k]

    S = _vb_set(lat)
    rowcols = _row_index(lat)
    gx, gw = np.polynomial.hermite_e.hermegauss(GH_N)
    gw = gw / gw.sum()
    T = lat.T.toarray()
    for c in configs:
        Lz_inv = sla.solve_triangular(c.ga.chol, np.eye(lat.n_z), lower=True)
        Sz = Lz_inv.T @ Lz_inv
        Sx = T @ Sz @ T.T
        _vb_correct(lat, model, c, Sx, S, rowcols, (gx, gw))
    lpw = np.array([c.log_post + c.log_weight for c in configs])
    probs = np.exp(lpw - lpw.max())
    probs /= probs.sum()
    info.update({"nconfig": len(configs), "n_theta": m, "vb_status": [c.vb_status for c in configs],
                 "vb_iter": [c.vb_iter for c in configs],
                 "newton_converged": all(c.ga.converged for c in configs)})
    return Fit(lat=lat, model=model, theta_mode=theta_mode, hessian=H, V=V, lam=lam, corr_pos=corr_pos,
               corr_neg=corr_neg, configs=configs, probs=probs, info=info)


# ---------------------------------------------------------------- 5. predictive draws
def sample_predictor(fit: Fit, n: int, rng: np.random.Generator, rows: np.ndarray):
    """n draws of (size, linear predictor at `rows`, offset included), as
    inla.posterior.sample + inla.posterior.sample.eval give c(theta[1], Predictor[rows])."""
    lat = fit.lat
    k = np.sort(rng.choice(len(fit.configs), size=n, p=fit.probs))
    A_rows = lat.A[rows] @ lat.T
    size = np.empty(n)
    eta = np.empty((len(rows), n))
    for ci in np.unique(k):
        c = fit.configs[ci]
        js = np.flatnonzero(k == ci)
        # centre: the VB-corrected mean projected onto the constraint subspace (JC-28)
        zmean = lat.T.T @ c.mean_x
        eps = rng.standard_normal((lat.n_z, len(js)))
        zs = zmean[:, None] + sla.solve_triangular(c.ga.chol.T, eps, lower=False)
        eta[:, js] = (A_rows @ zs) + lat.offset[rows][:, None]
        size[js] = np.exp(c.theta[0])
    return size, eta


# ---------------------------------------------------------------- summaries (L3 files)
HYPER_NAMES = ["size for the nbinomial observations (1/overdispersion)", "Precision for ID_spat",
               "Precision for ID_time_cyclic", "Precision for ID_time_cyclic2"]


def write_summaries(fit: Fit, mf, out: Path, seed: int, n_hyper_draws: int = 200000) -> None:
    """The fit's summaries in the files and names the instrumented R reference writes, so
    04_fidelityMetrics compares both alike."""
    out.mkdir(parents=True, exist_ok=True)
    lat = fit.lat
    m = lat.n_theta
    # hyperparameters on the natural scale: the asymmetric Gaussian INLA's design is built
    # on (split normal per z axis, sds corr_pos / corr_neg), by Monte Carlo (JC-28)
    rng = np.random.default_rng(seed + 1)
    z = rng.standard_normal((n_hyper_draws, m))
    z = np.where(z > 0, z * fit.corr_pos, z * fit.corr_neg)
    th = fit.theta_mode + z @ (fit.V / np.sqrt(fit.lam)).T
    nat = np.exp(th)
    hp = pd.DataFrame({"name": HYPER_NAMES[:m], "mean": nat.mean(axis=0), "sd": nat.std(axis=0, ddof=1),
                       "0.025quant": np.quantile(nat, 0.025, axis=0), "0.5quant": np.quantile(nat, 0.5, axis=0),
                       "0.975quant": np.quantile(nat, 0.975, axis=0)})
    hp.to_csv(out / "hyperpar.csv", index=False)
    # latent: mixture over configs of Gaussians N(VB mean, GA variance)
    P = fit.probs
    means = np.array([c.mean_x for c in fit.configs])
    vars_ = np.array([c.sd_x ** 2 for c in fit.configs])
    mean = P @ means
    sd = np.sqrt(np.maximum(P @ (vars_ + means ** 2) - mean ** 2, 0))
    fb = lat.blocks["fixed"]
    pd.DataFrame({"name": mf.fixed_names, "mean": mean[fb], "sd": sd[fb]}).to_csv(out / "fixed.csv", index=False)
    terms = [("ID_spat", "u", lat.n_spat), ("ID_time_cyclic", "s", lat.n_cyc)]
    if lat.region_seasonal:
        terms.append(("ID_time_cyclic2", "s2", lat.n_cyc))
    for name, block, n in terms:
        b = lat.blocks[block]
        ids = np.tile(np.arange(1, n + 1), (b.stop - b.start) // n)
        if block != "u":
            ids = np.tile(mf.cyc_values, (b.stop - b.start) // n)
        pd.DataFrame({"ID": ids, "mean": mean[b], "sd": sd[b]}).to_csv(out / f"random_{name}.csv", index=False)
    pd.DataFrame([{**{f"theta_{i + 1}": t for i, t in enumerate(c.theta)},
                   "log_posterior": c.log_post + c.log_weight, "log_posterior_orig": c.log_post,
                   "vb_status": c.vb_status, "vb_iter": c.vb_iter} for c in fit.configs]).assign(
        log_posterior=lambda d: d.log_posterior - d.log_posterior_orig.max(),
        log_posterior_orig=lambda d: d.log_posterior_orig - d.log_posterior_orig.max(),
    ).to_csv(out / "configs.csv", index=False)
    info = {"engine": "ewars_python.inla_approx (candidate a)", "theta_mode": [float(t) for t in fit.theta_mode],
            "nconfig": fit.info["nconfig"], "n_theta": m, "mode_status": 0, "seed": int(seed),
            "corr_pos": fit.corr_pos.tolist(), "corr_neg": fit.corr_neg.tolist(),
            **{k: v for k, v in fit.info.items() if k not in ("nconfig", "n_theta")}}
    (out / "fit_info.json").write_text(json.dumps(info, indent=2))
