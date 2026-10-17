# r-inla-gmrflib (GMRFLib, INLA's approximation engine)
(IS_SHADOW)

Fetched in batch 8 of the plan `26-10-14_pythonEwarsForChap` by
`AI-internal/data-acquisition/fetch_gmrflib_sources.sh`, at the same r-inla commit as
`Archive/r-sources/r-inla/` (tag `Version_25.10.19`, the version the R reference runs).
Never edited.

- `src/gmrflib/` — every `.c` and `.h` file under `gmrflib/`: the hyperparameter mode search,
  the CCD integration design, the skewness-corrected standard deviations, the VB
  correction and the posterior sampler. Inference candidate (a) follows these as its
  specification.
- `commit.txt`, `sha256sums.txt` — the commit, and a checksum per file.
