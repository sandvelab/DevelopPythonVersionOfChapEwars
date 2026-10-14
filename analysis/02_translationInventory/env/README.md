# env — the R reference image, for this node's two R scripts

`extract_r_calls.R` and `inla_defaults.R` must read the packages the reference actually runs
(INLA 25.10.19, dlnm 2.4.10, R 4.5.0), so they run inside the reference image,
`ghcr.io/chap-models/chapkit_ewars_model@sha256:959fb4f0f1b9d257a9697925f4500fd8ec4ffa9e1bb3ed7fc36e4f5c57c6ff88`
(linux/amd64; on Apple Silicon under emulation). `build_inventory.py` runs under the project
main environment (`environment/`).
