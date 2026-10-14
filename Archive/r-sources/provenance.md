# Provenance — r-sources
(IS_SHADOW)

All three folders: fetched 2026-10-14 by `bash AI-internal/data-acquisition/fetch_r_sources.sh`
(log: `AI-internal/data-acquisition/fetch_r_sources.log`); checksums in each folder's
`sha256sums.txt`. Information: agent-retrieved; the folders' contents were chosen to cover the
plan's §4 list (inla.scale.model, the cyclic rw1 and iid definitions, the nbinomial likelihood
and prior documentation, inla.posterior.sample) plus dlnm.

## reference-image/
- source: `ghcr.io/chap-models/chapkit_ewars_model@sha256:959fb4f0f1b9d257a9697925f4500fd8ec4ffa9e1bb3ed7fc36e4f5c57c6ff88`, linux/amd64
- produced by: `AI-internal/data-acquisition/dump_reference_image.R`, run in the image
- versions found: INLA 25.10.19, dlnm 2.4.10, R 4.5.0 (`package_versions.tsv`)
- licence: as the packages' (INLA: MIT + file LICENSE, per `INLA_DESCRIPTION`; dlnm: GPL (>= 2); R base and splines/stats: GPL-2 | GPL-3)

## r-inla/src/
- source: https://github.com/hrue/r-inla.git, tag `Version_25.10.19`, commit `acb55f3748be94ca49e9c81a85df8975241f742a` (`commit.txt`)
- selection: paths matching `rinla/R/`, `inlaprog/src/`, `gmrflib/rw.[ch]`, `r-inla.org/doc/{latent,likelihood,prior,hyper}/**.tex`, LICENSE/COPYING
- licence: MIT (`src/LICENSE`, "Copyright 2025 Haavard Rue"; the installed package declares `MIT + file LICENSE`)
- note: the tag matches the installed version string; the installed code is also deparsed
  in `reference-image/installed_functions/` for the functions used, as a cross-check.

## dlnm/
- source: https://cran.r-project.org/src/contrib/dlnm_2.4.10.tar.gz, sha256 `3b75be8ce30b41c90a7b01f373d7a4ca9c5ddddb1739c5e6763c66ac2dfb0bf2`
- licence: GPL (>= 2) (dlnm/DESCRIPTION)
