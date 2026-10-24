"""The Gaussian approximation of the latent field at one hyperparameter value, and the
Laplace approximation of the hyperparameters' log posterior built on it.

At theta, the mode z* of log p(z | y, theta) is found by Newton's method, and the
Gaussian approximation N(z*, Q*^{-1}) with Q* = Q(theta) + A_z' W A_z is taken there
(W: minus the second derivative of the log-likelihood in eta, at the mode). Then

    log p(theta | y) = log p(theta) + 1/2 log|Q(theta)| - 1/2 z*' Q(theta) z*
                       + sum_i log p(y_i | eta_i*) - 1/2 log|Q*|   + const,

the Laplace approximation of Rue, Martino and Chopin (2009), in the constrained
coordinates z (latent.py), where it is exact for the constraints.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import scipy.linalg as sla

from .latent import Latent
from .primitives import log_prior_loggamma, log_prior_pc_mgamma, nb_grad_hess, nb_loglik


def log_prior_theta(theta: np.ndarray) -> float:
    """INLA's default hyperpriors (inla_defaults.tsv): pc.mgamma(7) on log size,
    loggamma(1, 5e-05) on every log precision."""
    return log_prior_pc_mgamma(theta[0], 7.0) + sum(log_prior_loggamma(t, 1.0, 5e-05) for t in theta[1:])


@dataclass
class GaussApprox:
    theta: np.ndarray
    z: np.ndarray  # mode, constrained coordinates
    chol: np.ndarray  # lower Cholesky factor of Q*
    log_post: float  # unnormalised Laplace log posterior of theta
    eta: np.ndarray  # linear predictor at the mode, offset included
    newton_iter: int
    converged: bool


class LaplaceModel:
    def __init__(self, lat: Latent):
        self.lat = lat
        self.Az_obs = None
        A_obs = lat.A[lat.obs]
        self.A_obs = A_obs.tocsr()
        self.A_obs_T = A_obs.T.tocsr()
        self.Tt = lat.T.T.tocsr()
        self.y_obs = lat.y[lat.obs]
        self.off_obs = lat.offset[lat.obs]
        self._z_warm = np.zeros(lat.n_z)

    # x = T z ; eta = A x + offset
    def eta_all(self, z: np.ndarray) -> np.ndarray:
        return self.lat.A @ (self.lat.T @ z) + self.lat.offset

    def _hess_z(self, w: np.ndarray) -> np.ndarray:
        """A_z' W A_z for the observed rows, as T' (A' W A) T."""
        H = (self.A_obs_T @ self.A_obs.multiply(w[:, None])).toarray()
        HT = (self.Tt @ H.T).T  # H @ T as (T' H')'
        return np.asarray(self.Tt @ HT)

    def approx(self, theta: np.ndarray, z0: np.ndarray | None = None, tol: float = 1e-10,
               max_iter: int = 200) -> GaussApprox:
        lat = self.lat
        size = np.exp(theta[0])
        Q = lat.prior_precision_z(theta)
        z = (self._z_warm if z0 is None else z0).copy()

        def objective(zz):
            eta = self.A_obs @ (lat.T @ zz) + self.off_obs
            return float(np.sum(nb_loglik(self.y_obs, eta, size)) - 0.5 * zz @ Q @ zz), eta

        f, eta = objective(z)
        converged = False
        for it in range(1, max_iter + 1):
            g, w = nb_grad_hess(self.y_obs, eta, size)
            grad = self.Tt @ (self.A_obs_T @ g) - Q @ z
            P = Q + self._hess_z(w)
            L = sla.cholesky(P, lower=True)
            step = sla.cho_solve((L, True), grad)
            # backtracking line search on the (concave) log posterior of z
            t = 1.0
            while True:
                z_new = z + t * step
                f_new, eta_new = objective(z_new)
                if f_new >= f - 1e-12 * abs(f) or t < 1e-8:
                    break
                t *= 0.5
            dz = np.max(np.abs(z_new - z))
            z, f, eta = z_new, f_new, eta_new
            if dz < tol * max(1.0, np.max(np.abs(z))):
                converged = True
                break
        g, w = nb_grad_hess(self.y_obs, eta, size)
        P = Q + self._hess_z(w)
        L = sla.cholesky(P, lower=True)
        logdet_P = 2.0 * np.sum(np.log(np.diag(L)))
        log_post = (log_prior_theta(theta) + 0.5 * lat.prior_logdet_z(theta) - 0.5 * z @ Q @ z
                    + float(np.sum(nb_loglik(self.y_obs, eta, size))) - 0.5 * logdet_P)
        self._z_warm = z
        return GaussApprox(theta=np.array(theta, dtype=float), z=z, chol=L, log_post=float(log_post),
                           eta=self.eta_all(z), newton_iter=it, converged=converged)

    def log_post(self, theta: np.ndarray) -> float:
        """The Laplace log posterior, or -inf where the Gaussian approximation fails
        (an optimiser's trial step far outside the posterior's support)."""
        theta = np.asarray(theta, dtype=float)
        if not np.all(np.isfinite(theta)) or np.max(np.abs(theta)) > 30:
            return -np.inf
        try:
            with np.errstate(all="ignore"):
                ga = self.approx(theta)
        except (np.linalg.LinAlgError, ValueError):
            self._z_warm = np.zeros(self.lat.n_z)
            return -np.inf
        if not np.isfinite(ga.log_post):
            self._z_warm = np.zeros(self.lat.n_z)
            return -np.inf
        return ga.log_post
