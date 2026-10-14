# env — the evaluation platform for this node

This node runs no project analysis code; it drives chap-core. Its environment is
therefore chap-core's own, not the project main environment:

- **chap-core** at commit `b8c8f788fbc011f3d9d8a18ba9e993725023a6e4`, installed with
  `uv sync --frozen --no-dev --python 3.13` from chap-core's own `uv.lock` at that commit.
  `scripts/run_reference_through_chap.sh` clones and installs it afresh on every run, into
  `work/<run>/chap-core/` (gitignored); the commit it used is written to
  `results/<run>/chap_core_commit.txt`.
- **The R reference**: `ghcr.io/chap-models/chapkit_ewars_model@sha256:959fb4f0f1b9d257a9697925f4500fd8ec4ffa9e1bb3ed7fc36e4f5c57c6ff88`
  (tag `sha-964eea8`, linux/amd64), which reports git revision
  `964eea8bfdb194ca8985723216e94f1ac63aa4f1` on `/api/v1/info`; recorded per run in
  `results/<run>/service_info.json` and `image_digest.txt`.

`uv sync --frozen` was chosen over the docs' `uv tool install chap-core`, which installs
the latest PyPI release with unpinned dependencies (JC-03).
