# environment

The **one main environment** for the whole analysis, used generally. A node overrides it
only where it genuinely needs something else, in that node's `env/`, with the reason
recorded in that node's `claim.md`.

| File | What it is |
|---|---|
| `environment.yml` | Declarative — the interpreter version and the libraries the analysis asks for, one line each, with a comment saying what each is for. |
| `install-env.sh` | The build. Creates `env/` **from `lock.txt`**, and re-resolves from `environment.yml` only with `RESOLVE=1`, reporting any difference between what it built and the lockfile. Uses `uv`. |
| `lock.txt` | Resolved — every package with its exact version (`uv pip freeze`). **This is what reproduces.** Written by `RESOLVE=1 bash environment/install-env.sh`, which is what `/pin-environment` runs. Absent in a fresh copy. |
| `Dockerfile` | The image layer, where the analysis matters enough to outlive its dependencies or depends on a platform-specific runner. Absent until a project decides it needs one, and the decision is recorded here either way. |
| `env/` | The built environment. Not tracked; rebuild with `install-env.sh`. |

Invoke directly, as `environment/env/bin/python` — never by activating it — matching the
convention `AGENTS.md` §8 sets for `.venv`. Note this is *not* the `.venv` at the repository
root, which runs the repository's own machinery (`node.py`, `check_invariants.py`). A node's
`run.sh` sets `PYTHON` to this interpreter; `node.py` writes that line.

## Pinned

Pinned 2026-10-14 in batch 3, from the translation inventory (JC-12): Python 3.13.0, numpy,
scipy, pandas, pyyaml, and dlnmpy at commit `8c5edd79` (0.8.4). Verified by the two-pass
check: `RESOLVE=1 bash environment/install-env.sh` wrote `lock.txt` (7 packages), and a clean
rebuild from it reported "Built environment matches environment/lock.txt exactly". The
inference libraries are added, and the lock re-resolved, when batches 8–10 build the
inference candidates. No `Dockerfile` yet: the Python service gets its own image in batch 11.

Re-pinned 2026-10-18 in batch 9: numpyro added for inference candidate (b), bringing jax
and jaxlib 0.11.2. `RESOLVE=1` left every earlier pin unchanged (only additions in the
lockfile diff), and a clean rebuild reported "Built environment matches
environment/lock.txt exactly". Candidate (a) uses none of the added packages. The service
image of batch 11 does not include them (its own `uv.lock`).

## Say what cannot be pinned

A vanished data source, a licence server, a specific GPU, an evaluation platform run as a
hosted service — none of this survives pinning. Where such a dependency exists, state it here
plainly rather than leaving a reproducer to discover it.

Here: the R reference runs as a Docker image pinned by digest, which outlives a vanished
registry only if the image is kept locally (`docker save`); the image is not archived in this
repository.
