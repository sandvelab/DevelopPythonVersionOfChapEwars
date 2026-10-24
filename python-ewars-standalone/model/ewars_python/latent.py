"""The latent Gaussian model INLA fits, written out (shared by every inference candidate).

    y_i ~ NB(mu_i, size),  log mu_i = log E_i + eta_i
    eta = b0 + X beta + u[ID_spat, ID_year] + s[ID_time_cyclic] (+ s2[ID_time_cyclic, ID_spat])

Latent field x, in INLA's order (formula terms, then fixed effects):
    u   iid, precision tau_u, one block of n_spat values per ID_year (replicate)
    s   cyclic RW1 with scale.model, precision tau_s, sum-to-zero
    s2  (region_seasonal) cyclic RW1 with scale.model, precision tau_s2, one block per
        ID_spat (replicate), sum-to-zero within each block
    b0  intercept, prior precision 1e-4;  beta  basis coefficients, prior precision `precision`

Hyperparameters theta = (log size, log tau_u, log tau_s[, log tau_s2]), INLA's internal scale.

The constraints are made exact by writing each constrained block as x = T z with T an
orthonormal basis of the sum-to-zero subspace (primitives.sum_to_zero_basis); in z the
model is an ordinary proper Gaussian.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import scipy.sparse as sp

from .frame import ModelFrame
from .primitives import cyclic_rw1_scale, cyclic_rw1_structure, sum_to_zero_basis

PREC_INTERCEPT = 1e-4  # control.fixed(prec.intercept = 1e-4), predict.R
# f() adds 1e-4, unscaled, to the diagonal of every model with constr = TRUE, so to every
# cyclic RW1 block here (rinla/R/f.R:861-867, set.default.arguments.R:229-230; gmrflib/pre-opt.c:856)
RW1_DIAGONAL = 1e-4


@dataclass
class Latent:
    n_spat: int
    n_year: int
    n_cyc: int
    region_seasonal: bool
    p_fixed: int
    precision: float
    A: sp.csr_matrix  # n_rows x n_x, full coordinates
    T: sp.csr_matrix  # n_x x n_z, x = T z
    blocks: dict  # name -> slice in x
    zblocks: dict  # name -> slice in z
    offset: np.ndarray
    y: np.ndarray
    obs: np.ndarray  # boolean, rows with observed cases
    RT: np.ndarray  # T_n' R_scaled T_n for one cyclic RW1 block ((n_cyc-1) square)
    R_scaled: np.ndarray  # scale.model factor times the cyclic RW1 structure matrix

    @property
    def n_theta(self) -> int:
        return 4 if self.region_seasonal else 3

    @property
    def n_x(self) -> int:
        return self.A.shape[1]

    @property
    def n_z(self) -> int:
        return self.T.shape[1]

    def prior_precision_z(self, theta: np.ndarray) -> np.ndarray:
        """Dense prior precision of z at theta (block diagonal)."""
        Q = np.zeros((self.n_z, self.n_z))
        tau_u, tau_s = np.exp(theta[1]), np.exp(theta[2])
        zu = self.zblocks["u"]
        Q[zu, zu] = np.eye(zu.stop - zu.start) * tau_u
        zs = self.zblocks["s"]
        Q[zs, zs] = tau_s * self.RT + RW1_DIAGONAL * np.eye(self.n_cyc - 1)
        if self.region_seasonal:
            tau_s2 = np.exp(theta[3])
            m = self.n_cyc - 1
            start = self.zblocks["s2"].start
            for j in range(self.n_spat):
                b = slice(start + j * m, start + (j + 1) * m)
                Q[b, b] = tau_s2 * self.RT + RW1_DIAGONAL * np.eye(m)
        zf = self.zblocks["fixed"]
        d = np.full(self.p_fixed, self.precision)
        d[0] = PREC_INTERCEPT
        Q[zf, zf] = np.diag(d)
        return Q

    def prior_logdet_z(self, theta: np.ndarray) -> float:
        """Twice the log normalising constant of the latent prior, as INLA counts it:
        (N - r) theta per replicate of each term (iid: r = 0; cyclic RW1: r = 1), and
        nothing for the structure matrix's pseudo-determinant, the scaling or the 1e-4
        diagonal, which INLA leaves out as constant in theta (inlaprog/src/inla.c extra(),
        2920-2948). The fixed effects' constant is left out likewise."""
        m = self.n_cyc - 1
        ld = self.n_spat * self.n_year * theta[1] + m * theta[2]
        if self.region_seasonal:
            ld += self.n_spat * m * theta[3]
        return float(ld)

    def prior_precision_x(self, theta: np.ndarray) -> np.ndarray:
        """Dense prior precision of x in full coordinates (INLA's Q_0), constraints not
        applied; used by the VB mean correction."""
        Q = np.zeros((self.n_x, self.n_x))
        b = self.blocks["u"]
        Q[b, b] = np.eye(b.stop - b.start) * np.exp(theta[1])
        n = self.n_cyc
        Rs = self.R_scaled
        b = self.blocks["s"]
        Q[b, b] = np.exp(theta[2]) * Rs + RW1_DIAGONAL * np.eye(n)
        if self.region_seasonal:
            start = self.blocks["s2"].start
            for j in range(self.n_spat):
                bb = slice(start + j * n, start + (j + 1) * n)
                Q[bb, bb] = np.exp(theta[3]) * Rs + RW1_DIAGONAL * np.eye(n)
        b = self.blocks["fixed"]
        d = np.full(self.p_fixed, self.precision)
        d[0] = PREC_INTERCEPT
        Q[b, b] = np.diag(d)
        return Q


def build_latent(mf: ModelFrame, precision: float) -> Latent:
    n_rows = len(mf.y)
    n_spat = int(mf.spat.max())
    n_year = int(mf.year.max())
    cyc_values = mf.cyc_values
    n_cyc = len(cyc_values)
    # INLA places the cyclic RW1 nodes at the sorted distinct values; this port assumes
    # they are consecutive integers, as months 1..12 and weeks 1..52/53 are (JC-22)
    if not np.array_equal(cyc_values, np.arange(cyc_values[0], cyc_values[0] + n_cyc)):
        raise ValueError(f"cyclic index values are not consecutive integers: {cyc_values}")
    cyc_idx = np.searchsorted(cyc_values, mf.cyc)
    p = mf.X.shape[1]

    sizes = {"u": n_spat * n_year, "s": n_cyc}
    if mf.region_seasonal:
        sizes["s2"] = n_cyc * n_spat
    sizes["fixed"] = p
    blocks, start = {}, 0
    for k, v in sizes.items():
        blocks[k] = slice(start, start + v)
        start += v
    n_x = start

    rows = np.arange(n_rows)
    cols_u = blocks["u"].start + (mf.year - 1) * n_spat + (mf.spat - 1)  # (r-1)*n + j, CH-22
    cols_s = blocks["s"].start + cyc_idx
    parts = [sp.csr_matrix((np.ones(n_rows), (rows, cols_u)), shape=(n_rows, n_x)),
             sp.csr_matrix((np.ones(n_rows), (rows, cols_s)), shape=(n_rows, n_x))]
    if mf.region_seasonal:
        cols_s2 = blocks["s2"].start + (mf.spat - 1) * n_cyc + cyc_idx
        parts.append(sp.csr_matrix((np.ones(n_rows), (rows, cols_s2)), shape=(n_rows, n_x)))
    Xfull = sp.lil_matrix((n_rows, n_x))
    Xfull[:, blocks["fixed"]] = mf.X
    parts.append(Xfull.tocsr())
    A = sum(parts[1:], parts[0]).tocsr()

    Tn = sum_to_zero_basis(n_cyc)
    Tblocks = [sp.identity(sizes["u"]), sp.csr_matrix(Tn)]
    zsizes = {"u": sizes["u"], "s": n_cyc - 1}
    if mf.region_seasonal:
        Tblocks.append(sp.block_diag([sp.csr_matrix(Tn)] * n_spat))
        zsizes["s2"] = (n_cyc - 1) * n_spat
    Tblocks.append(sp.identity(p))
    zsizes["fixed"] = p
    T = sp.block_diag(Tblocks).tocsr()
    zblocks, start = {}, 0
    for k, v in zsizes.items():
        zblocks[k] = slice(start, start + v)
        start += v

    Rs = cyclic_rw1_scale(n_cyc) * cyclic_rw1_structure(n_cyc)
    RT = Tn.T @ Rs @ Tn
    RT = (RT + RT.T) / 2
    obs = ~np.isnan(mf.y)
    return Latent(n_spat=n_spat, n_year=n_year, n_cyc=n_cyc, region_seasonal=mf.region_seasonal,
                  p_fixed=p, precision=precision, A=A, T=T, blocks=blocks, zblocks=zblocks,
                  offset=mf.offset, y=mf.y, obs=obs, RT=RT, R_scaled=Rs)
