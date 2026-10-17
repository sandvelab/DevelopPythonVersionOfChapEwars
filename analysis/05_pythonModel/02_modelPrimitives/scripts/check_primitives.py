"""The Python primitives against the values INLA and R compute (inla_primitives.R).

Usage: check_primitives.py <inla values dir> <package dir> <out tsv>
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

inla, package, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
sys.path.insert(0, str(package))
from ewars_python.primitives import (cyclic_rw1_scale, cyclic_rw1_structure, log_prior_pc_mgamma,  # noqa: E402
                                     nb_loglik, sum_to_zero_basis)

rows = []
sc = pd.read_csv(inla / "inla_cyclic_rw1_scale.tsv", sep="\t")
for r in sc.itertuples():
    py = cyclic_rw1_scale(int(r.n))
    rows.append(("cyclic_rw1_scale", f"n={r.n}", r.factor, py, abs(py - r.factor) / abs(r.factor)))
pc = pd.read_csv(inla / "inla_pc_mgamma.tsv", sep="\t")
for r in pc.itertuples():
    py = log_prior_pc_mgamma(r.theta)
    rows.append(("pc_mgamma_log_density", f"theta={r.theta}", r.log_density, py, abs(py - r.log_density)))
nb = pd.read_csv(inla / "r_dnbinom.tsv", sep="\t")
for r in nb.itertuples():
    py = float(nb_loglik(np.array([r.y]), np.array([r.eta]), r.size)[0])
    rows.append(("nb_loglik", f"y={r.y},eta={r.eta},size={r.size}", r.loglik, py, abs(py - r.loglik)))
# structural facts: the constraint basis is orthonormal and orthogonal to 1; the structure
# matrix has the constant vector as its null space
for n in (12, 52, 53):
    T = sum_to_zero_basis(n)
    for q, v in (("sum_to_zero_basis_orthonormality", np.max(np.abs(T.T @ T - np.eye(n - 1)))),
                 ("sum_to_zero_basis_sums", np.max(np.abs(T.sum(axis=0)))),
                 ("rw1_null_space", np.max(np.abs(cyclic_rw1_structure(n) @ np.ones(n))))):
        rows.append((q, f"n={n}", 0.0, float(v), float(v)))
df = pd.DataFrame(rows, columns=["quantity", "at", "reference", "python", "abs_or_rel_diff"])
df.to_csv(out, sep="\t", index=False)
print(df.groupby("quantity")["abs_or_rel_diff"].max().to_string())
