"""Inference candidate (b): the EWARS model sampled by NUTS (NumPyro), the same model and
priors candidate (a) approximates.

The target is the joint density of (theta, x) whose Laplace approximation is
ewars_python.laplace: the NB likelihood on the observed rows, INLA's default hyperpriors on
INLA's internal scale, and the latent Gaussian of ewars_python.latent, with INLA's 1e-4 RW1
diagonal and the prior normalising constant counted as INLA counts it
(Latent.prior_logdet_z). Where this posterior differs from candidate (a)'s or from INLA's,
the difference is the approximation, not the model. check_target.py verifies the identity.

Parametrisation (the same distribution; chosen for NUTS's geometry, JC-33). Two are
available, as Target(parametrisation=...):
  "split" (used): the intercept and the iid effect u share one direction the likelihood
    cannot see (b0 + c, u - c), so they are sampled as
      ubar = r_bar / sqrt(n_u tau_u)          (the mean of u; prior only)
      w    ~ N(0, 1/tau_u), n_u - 1 values    (u's deviations: u = ubar + T_u w)
      a    ~ N(ubar, 1/1e-4)                  (the level b0 + ubar the data see; b0 = a - ubar)
    with T_u the orthonormal sum-to-zero basis of primitives.sum_to_zero_basis. The map to
    (b0, u) is linear, so the joint density is the same up to the Jacobian tau_u^(-1/2).
  "centred": u sampled directly, N(0, 1/tau_u), and b0 with the other fixed effects.
The other terms are the same in both:
    s_z    = V diag(tau_s lam + 1e-4)^(-1/2) r_s,   T_n' R_scaled T_n = V diag(lam) V'
    s2_z   likewise per location block, with tau_s2
    b0     = r_0 / sqrt(1e-4),  beta = r_b / sqrt(precision)
with every r standard normal, and the sum-to-zero constraints exact through T_n (as in
latent.py). The exact Gaussian's normalising constant, 1/2 sum log(tau lam + 1e-4), is
replaced by INLA's 1/2 m log tau through a factor, so that the target is candidate (a)'s
to the last term.
"""

from __future__ import annotations

import numpy as np
import numpyro

numpyro.set_host_device_count(4)  # one CPU device per chain; must precede JAX's first use

import jax  # noqa: E402
import jax.numpy as jnp  # noqa: E402
from jax.scipy.special import digamma, gammaln, polygamma  # noqa: E402

jax.config.update("jax_enable_x64", True)

import numpyro.distributions as dist  # noqa: E402
from numpyro.infer import MCMC, NUTS, init_to_value  # noqa: E402

# INLA's initial values of theta, which candidate (a) also starts from
from ewars_python.inla_approx import INITIAL_LOG_PREC, INITIAL_LOG_SIZE  # noqa: E402
from ewars_python.latent import PREC_INTERCEPT, RW1_DIAGONAL, Latent  # noqa: E402
from ewars_python.primitives import sum_to_zero_basis  # noqa: E402


def log_prior_theta(theta):
    """ewars_python.laplace.log_prior_theta in JAX: pc.mgamma(7) on log size,
    loggamma(1, 5e-05) on each log precision (primitives.log_prior_pc_mgamma,
    log_prior_loggamma, including the series for size > 1e4)."""
    lam = 7.0
    x = -theta[0]
    a = jnp.exp(x)
    v = 1.0 / a
    d = jnp.sqrt(2.0 * (jnp.log(v) - digamma(v)))
    special_big = -2.0 * jnp.log(v) - jnp.log(2.0) + 1.0 / (3.0 * v) - 1.0 / (18.0 * v ** 2) - 22.0 / (405.0 * v ** 3)
    vs = jnp.minimum(v, 1.0e4)
    special_small = jnp.log(polygamma(1, vs) - 1.0 / vs)
    special = jnp.where(v > 1.0e4, special_big, special_small)
    lp = jnp.log(lam) - lam * d - 2.0 * jnp.log(a) - jnp.log(d) + special + x
    a_g, b_g = 1.0, 5e-05
    lg = a_g * jnp.log(b_g) - gammaln(a_g) + a_g * theta[1:] - b_g * jnp.exp(theta[1:])
    return lp + jnp.sum(lg)


def nb_loglik(y, eta, size):
    """ewars_python.primitives.nb_loglik in JAX."""
    ls = jnp.log(size)
    lse = jnp.logaddexp(ls, eta)
    return gammaln(y + size) - gammaln(size) - gammaln(y + 1) + size * (ls - lse) + y * (eta - lse)


class Target:
    """One fit's data and fixed matrices as JAX arrays, the NumPyro model, and the map from
    the sampled coordinates back to the latent field x in INLA's full coordinates."""

    def __init__(self, lat: Latent, parametrisation: str = "split"):
        if parametrisation not in ("split", "centred"):
            raise ValueError(parametrisation)
        self.lat = lat
        self.parametrisation = parametrisation
        A = lat.A.tocsr()
        b = lat.blocks

        def col(block):  # A has exactly one 1 per row in each random-effect block
            return np.asarray(A[:, b[block]].argmax(axis=1)).ravel()

        self.idx_u = col("u")
        self.idx_s = col("s")
        self.idx_s2 = col("s2") if lat.region_seasonal else None
        self.X = A[:, b["fixed"]].toarray()
        self.offset = lat.offset
        self.obs = lat.obs
        self.m = lat.n_cyc - 1
        self.n_u = lat.n_spat * lat.n_year
        self.n_theta = lat.n_theta
        self.lam, V = np.linalg.eigh(lat.RT)
        self.TnV = sum_to_zero_basis(lat.n_cyc) @ V
        d = np.full(lat.p_fixed, lat.precision)
        d[0] = PREC_INTERCEPT
        self.fixed_sd = 1.0 / np.sqrt(d)
        J = jnp.asarray
        o = self.obs
        self.j = dict(idx_u=J(self.idx_u[o]), idx_s=J(self.idx_s[o]), X=J(self.X[o]), off=J(self.offset[o]),
                      y=J(lat.y[o]), TnV=J(self.TnV), lam=J(self.lam), fixed_sd=J(self.fixed_sd))
        if lat.region_seasonal:
            self.j["idx_s2"] = J(self.idx_s2[o])
        if parametrisation == "split":
            self.Tu = sum_to_zero_basis(self.n_u)
            self.j["Tu"] = J(self.Tu)

    def model(self):
        j, m, lat = self.j, self.m, self.lat
        theta = numpyro.sample("theta", dist.ImproperUniform(dist.constraints.real_vector, (), (self.n_theta,)))
        numpyro.factor("log_prior_theta", log_prior_theta(theta))
        size, tau_u, tau_s = jnp.exp(theta[0]), jnp.exp(theta[1]), jnp.exp(theta[2])
        if self.parametrisation == "split":
            ubar = numpyro.sample("r_bar", dist.Normal(0, 1)) / jnp.sqrt(self.n_u * tau_u)
            w = numpyro.sample("w", dist.Normal(0, 1 / jnp.sqrt(tau_u)).expand([self.n_u - 1]).to_event(1))
            a = numpyro.sample("a", dist.Normal(ubar, j["fixed_sd"][0]))
            u = ubar + j["Tu"] @ w
            r_f = (numpyro.sample("r_f", dist.Normal(0, 1).expand([lat.p_fixed - 1]).to_event(1))
                   if lat.p_fixed > 1 else jnp.zeros(0))
            r_f = jnp.concatenate([((a - ubar) / j["fixed_sd"][0])[None], r_f])
        else:
            u = numpyro.sample("u", dist.Normal(0, 1 / jnp.sqrt(tau_u)).expand([self.n_u]).to_event(1))
            r_f = numpyro.sample("r_f", dist.Normal(0, 1).expand([lat.p_fixed]).to_event(1))
        r_s = numpyro.sample("r_s", dist.Normal(0, 1).expand([m]).to_event(1))
        ev_s = tau_s * j["lam"] + RW1_DIAGONAL
        x_s = j["TnV"] @ (r_s / jnp.sqrt(ev_s))
        # INLA's normalising constant (m theta_s / 2) in place of the exact one
        corr = 0.5 * (m * theta[2] - jnp.sum(jnp.log(ev_s)))
        eta = j["off"] + u[j["idx_u"]] + x_s[j["idx_s"]] + j["X"] @ (r_f * j["fixed_sd"])
        if lat.region_seasonal:
            tau_s2 = jnp.exp(theta[3])
            r_s2 = numpyro.sample("r_s2", dist.Normal(0, 1).expand([lat.n_spat, m]).to_event(2))
            ev_s2 = tau_s2 * j["lam"] + RW1_DIAGONAL
            x_s2 = ((r_s2 / jnp.sqrt(ev_s2)) @ j["TnV"].T).reshape(-1)  # (spat - 1) * n_cyc + cyc, as latent.py
            eta = eta + x_s2[j["idx_s2"]]
            corr = corr + 0.5 * lat.n_spat * (m * theta[3]) - 0.5 * lat.n_spat * jnp.sum(jnp.log(ev_s2))
        numpyro.factor("inla_prior_constant", corr)
        numpyro.factor("loglik", jnp.sum(nb_loglik(j["y"], eta, size)))

    def latent_draws(self, samples: dict) -> np.ndarray:
        """x in INLA's full coordinates and block order (u, s[, s2], fixed), one row per draw."""
        th = np.asarray(samples["theta"])
        if self.parametrisation == "split":
            ubar = np.asarray(samples["r_bar"]) / np.sqrt(self.n_u * np.exp(th[:, 1]))
            u = ubar[:, None] + np.asarray(samples["w"]) @ self.Tu.T
            b0 = np.asarray(samples["a"]) - ubar
            rest = np.asarray(samples["r_f"]) if "r_f" in samples else np.zeros((len(th), 0))
            r_f = np.concatenate([(b0 / self.fixed_sd[0])[:, None], rest], axis=1)
        else:
            u = np.asarray(samples["u"])
            r_f = np.asarray(samples["r_f"])
        parts = [u]
        ev = np.exp(th[:, [2]]) * self.lam[None, :] + RW1_DIAGONAL
        parts.append((np.asarray(samples["r_s"]) / np.sqrt(ev)) @ self.TnV.T)
        if self.lat.region_seasonal:
            ev2 = np.exp(th[:, [3]]) * self.lam[None, :] + RW1_DIAGONAL
            r2 = np.asarray(samples["r_s2"]) / np.sqrt(ev2[:, None, :])
            parts.append((r2 @ self.TnV.T).reshape(len(th), -1))
        parts.append(r_f * self.fixed_sd[None, :])
        return np.concatenate(parts, axis=1)

    def eta_rows(self, x: np.ndarray, rows: np.ndarray) -> np.ndarray:
        """Linear predictor at `rows`, offset included: rows x draws."""
        return np.asarray(self.lat.A[rows] @ x.T) + self.offset[rows][:, None]

    def init_values(self) -> dict:
        th = np.full(self.n_theta, INITIAL_LOG_PREC)
        th[0] = INITIAL_LOG_SIZE
        return {"theta": jnp.asarray(th)}


def run_nuts(target: Target, seed: int, num_warmup: int, num_samples: int, num_chains: int) -> MCMC:
    """NUTS with NumPyro's defaults (target acceptance 0.8, diagonal mass matrix, tree depth
    10), chains in parallel on one CPU device each, started at INLA's initial theta."""
    kernel = NUTS(target.model, init_strategy=init_to_value(values=target.init_values()))
    mcmc = MCMC(kernel, num_warmup=num_warmup, num_samples=num_samples, num_chains=num_chains,
                chain_method="parallel", progress_bar=False)
    mcmc.run(jax.random.PRNGKey(seed), extra_fields=("diverging", "num_steps"))
    return mcmc
