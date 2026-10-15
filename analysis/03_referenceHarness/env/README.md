# env — the R reference image, and chap-core, for this node

`instrument_reference.R` runs inside the R reference image,
`ghcr.io/chap-models/chapkit_ewars_model@sha256:959fb4f0f1b9d257a9697925f4500fd8ec4ffa9e1bb3ed7fc36e4f5c57c6ff88`
(INLA 25.10.19, dlnm 2.4.10, R 4.5.0; linux/amd64, on Apple Silicon under emulation), because
the harness must record what the reference itself computes. `run_chap_repeats.sh` drives
chap-core at `b8c8f788`, installed from its own `uv.lock` into `work/`, exactly as node 01
does. The Python scripts run under the project main environment (`environment/`).
