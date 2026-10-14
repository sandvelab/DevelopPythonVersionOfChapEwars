# r-sources (R sources the Python port uses as design and test oracle)
(IS_SHADOW)

Fetched in batch 3 of the plan `26-10-14_pythonEwarsForChap` by
`AI-internal/data-acquisition/fetch_r_sources.sh`, at the versions installed in the R
reference image. Never edited.

- `reference-image/` — what the image runs: package versions, sessionInfo, the installed
  INLA's model definitions (`inla_models_selected.txt`) and control defaults, and the
  installed R code of the functions the model relies on, deparsed (`installed_functions/`).
- `r-inla/` — `hrue/r-inla` at tag `Version_25.10.19` (commit `acb55f37`): `rinla/R/`,
  `inlaprog/src/`, `gmrflib/rw.{c,h}` and the `.tex` documentation of latent models,
  likelihoods, priors and hyperparameters.
- `dlnm/` — the CRAN source tarball of dlnm 2.4.10, and its extracted tree.
