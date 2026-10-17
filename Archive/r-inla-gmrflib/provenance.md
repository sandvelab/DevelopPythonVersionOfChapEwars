# Provenance — r-inla-gmrflib
(IS_SHADOW)

## src/gmrflib/
- source: https://github.com/hrue/r-inla.git, commit `acb55f3748be94ca49e9c81a85df8975241f742a`
  (tag `Version_25.10.19`; the same commit as `Archive/r-sources/r-inla/commit.txt`)
- fetched: 2026-10-17 by `bash AI-internal/data-acquisition/fetch_gmrflib_sources.sh`
  (log: `AI-internal/data-acquisition/fetch_gmrflib_sources.log`)
- selection: every tracked path matching `gmrflib/*.c`, `gmrflib/*.h` (228 files, about 20 MB)
- licence: MIT, as the r-inla repository (`Archive/r-sources/r-inla/src/LICENSE`); the
  repository has no LICENSE file under `gmrflib/` itself
- information: agent-retrieved; fetched because `Archive/r-sources/` held only
  `gmrflib/rw.{c,h}`, and candidate (a) needs INLA's integration and sampling code
