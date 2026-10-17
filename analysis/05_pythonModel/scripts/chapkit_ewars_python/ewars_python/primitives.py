"""The INLA model pieces every inference candidate shares (batch 7).

Each is a port of the INLA 25.10.19 code the R reference runs (Archive/r-sources/,
Archive/r-inla-gmrflib/); the source is named beside each function.
"""

from __future__ import annotations

import numpy as np
from scipy.special import digamma, gammaln, polygamma

SQRT_DBL_EPSILON = np.sqrt(np.finfo(float).eps)  # GSL_SQRT_DBL_EPSILON


def cyclic_rw1_structure(n: int) -> np.ndarray:
    """Unscaled structure matrix of a cyclic first-order random walk on n nodes.

    gmrflib/rw.c GMRFLib_rw, cyclic case, order 1: 2 on the diagonal, -1 between cyclic
    neighbours (node 1 and node n are neighbours).
    """
    R = 2.0 * np.eye(n)
    for i in range(n):
        R[i, (i + 1) % n] -= 1.0
        R[(i + 1) % n, i] -= 1.0
    return R


def cyclic_rw1_scale(n: int) -> float:
    """The factor scale.model=TRUE multiplies the cyclic RW1 precision by.

    gmrflib/rw.c GMRFLib_rw_scale, cyclic case: the structure matrix multiplied by the
    guess n - 1, plus sqrt(DBL_EPSILON) on the diagonal, under the sum-to-zero constraint;
    the factor is the geometric mean of the constrained marginal variances times the guess.
    """
    guess = float(n - 1)
    Q = guess * cyclic_rw1_structure(n) + SQRT_DBL_EPSILON * np.eye(n)
    S = np.linalg.inv(Q)
    one = np.ones(n)
    S1 = S @ one
    Sc = S - np.outer(S1, S1) / (one @ S1)  # conditioning on sum(x) = 0
    return float(np.exp(np.mean(np.log(np.diag(Sc)))) * guess)


def sum_to_zero_basis(n: int) -> np.ndarray:
    """An n x (n - 1) orthonormal basis of {x : sum(x) = 0}.

    A constrained block is written x = T z, so that z is unconstrained and the
    constrained Gaussian is exact (no kriging correction needed).
    """
    # Helmert-type construction: deterministic, orthonormal, exactly orthogonal to 1
    T = np.zeros((n, n - 1))
    for k in range(1, n):
        T[:k, k - 1] = 1.0
        T[k, k - 1] = -k
        T[:, k - 1] /= np.sqrt(k * (k + 1))
    return T


def log_prior_loggamma(theta: float, a: float = 1.0, b: float = 5e-05) -> float:
    """loggamma(a, b) prior on theta = log(precision), as a density in theta.

    A Gamma(a, rate b) density on the precision tau = exp(theta), with the Jacobian:
    a log b - lgamma(a) + a theta - b exp(theta).
    """
    return a * np.log(b) - gammaln(a) + a * theta - b * np.exp(theta)


def log_prior_pc_mgamma(theta: float, lam: float = 7.0) -> float:
    """pc.mgamma prior on theta = log(size) of the negative binomial, as a density in theta.

    inlaprog/src/inla-priors.c priorfunc_pc_mgamma(theta) = priorfunc_pc_gamma(-theta):
    with a = exp(-theta), v = 1 / a = size, d = sqrt(2 (log v - psi(v))),
    log density = log lam - lam d - 2 log a - log d + SPECIAL(v) + log a, where
    SPECIAL(v) = log(psi_1(v) - 1 / v), replaced by its asymptotic series for v > 1e4.
    """
    x = -theta
    a = np.exp(x)
    v = 1.0 / a
    d = np.sqrt(2.0 * (np.log(v) - digamma(v)))
    if v > 1.0e4:
        special = -2.0 * np.log(v) - np.log(2.0) + 1.0 / (3.0 * v) - 1.0 / (18.0 * v ** 2) - 22.0 / (405.0 * v ** 3)
    else:
        special = np.log(polygamma(1, v) - 1.0 / v)
    return float(np.log(lam) - lam * d - 2.0 * np.log(a) - np.log(d) + special + x)


def nb_loglik(y: np.ndarray, eta: np.ndarray, size: float) -> np.ndarray:
    """Negative-binomial log-likelihood per observation, mean mu = exp(eta), size n.

    INLA's nbinomial (variant 0): mean mu, variance mu (1 + mu / n), the same as R's
    dnbinom(size = n, mu = mu) (CH-15, inventory).
    """
    mu = np.exp(eta)
    return (gammaln(y + size) - gammaln(size) - gammaln(y + 1)
            + size * (np.log(size) - np.logaddexp(np.log(size), eta))
            + y * (eta - np.logaddexp(np.log(size), eta)))


def nb_grad_hess(y: np.ndarray, eta: np.ndarray, size: float) -> tuple[np.ndarray, np.ndarray]:
    """First derivative and minus the second derivative of nb_loglik in eta."""
    mu = np.exp(eta)
    p = mu / (size + mu)
    grad = y - (y + size) * p
    w = (y + size) * p * (1.0 - p)
    return grad, w
