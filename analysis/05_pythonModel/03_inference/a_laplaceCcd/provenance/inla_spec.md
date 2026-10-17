result: results/inla_spec.md
script: ../../../../AI-internal/data-acquisition/fetch_gmrflib_sources.sh
        sha256:37c68d34bc277efc146140de4602160fa0ac8d5373a479114c4f9ec0a78efc35
invocation: written by a subagent of the batch 8 session, which read the archived sources (Archive/r-inla-gmrflib/, Archive/r-sources/) and cites file and line for each statement; copied unchanged from the session scratchpad. The script named is the fetch of the sources it read
inputs:
  ../../../../Archive/r-inla-gmrflib/sha256sums.txt  sha256:b968e2d7760c0fcc
  ../../../../Archive/r-sources/r-inla/sha256sums.txt  sha256:4996b7d954ae9966
environment: -
seeds: -
commit: 77a8482
instructions-commit: 400536d
node: analysis/05_pythonModel/03_inference/a_laplaceCcd
produced: 2026-10-17
alternatives-considered: Reading the sources in the main session: same information, delegated to keep it out of the main context. The spec marks three points UNRESOLVED (internal E with offset; VB strategy via base-R match.arg; the BFGS path)
agency: agent-autonomous
information: agent-retrieved
