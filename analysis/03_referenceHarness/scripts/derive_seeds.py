"""Derive the harness's component seeds from the project seed (readme-at-start.md).

Rule: seed(component) = 1 + (first 4 bytes of sha256("<project seed>/<component>"), big
endian) mod (2**31 - 2). The result is a positive integer below R's .Machine$integer.max,
so it is valid both for R's set.seed and for INLA's `seed` argument (which must be > 0 to
seed GMRFLib's sampler). One seed pair per replicate, shared across datasets and config
variants, so that replicate k of every variant draws from the same streams.

Usage: derive_seeds.py <project_seed> <n_replicates> <out_tsv>
"""

import hashlib
import sys

project_seed, n_rep, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]


def derive(component: str) -> int:
    h = hashlib.sha256(f"{project_seed}/{component}".encode()).digest()
    return 1 + int.from_bytes(h[:4], "big") % (2**31 - 2)


with open(out, "w") as f:
    f.write("replicate\tr_component\tr_seed\tinla_component\tinla_seed\n")
    for k in range(1, n_rep + 1):
        rc, ic = f"referenceHarness/rep{k}/R", f"referenceHarness/rep{k}/INLA"
        f.write(f"rep{k}\t{rc}\t{derive(rc)}\t{ic}\t{derive(ic)}\n")
print(open(out).read(), end="")
