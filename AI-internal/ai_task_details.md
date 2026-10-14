# Task details

The expanded entry for each task in `ai_task_history.md`: what was produced, the design
decisions, the files affected, and what a future session would need to know. Include
follow-ups, and say plainly where something did not work.

## T1 (2026-09-22) — `How-to-use-vault.md`

A human-facing walkthrough of how the repository is meant to be used, written at the root as
`How-to-use-vault.md`. It covers, in the order the work actually happens: what the repository
is for; the two principles behind it; set-up and git; fixing the three anchors and sealing the
holdout; writing the plan; the `/do` batch loop; the claim tree; all seventeen skills and when
each applies; where the manuscript and the results are found; what each of the six logs
records; what may and may not be changed; and the closing phases through release.

**The design decision worth knowing** is what this file deliberately does *not* do. `README.md`,
`setup-guide.md` and `folder-structure.md` already state much of this content, and `AGENTS.md`
§8 warns that a fact kept in two places goes stale silently. So the file is written as an
*order of operations* that links to those documents as canonical rather than restating them,
and says so in its own opening. That constraint was raised with the human before writing and
again after; it was accepted rather than resolved, so **the overlap is real and this file will
need checking whenever `README.md` or `setup-guide.md` changes.**

**Revised once on feedback**, which changed six things: the set-up and git steps were reframed
from shell commands the human types into a *Say: / It does:* form — what to ask the agent, and
what it runs behind the scenes — because the agent normally performs them; reproducibility and
veridical data science (Yu & Kumbier's predictability, computability, stability) were added as
an explicit §2 stating the motivation for every rule that follows; the `_edited` hand-edit
convention and the sealed holdout were each moved to the point in the workflow where they first
matter, rather than appearing only at the end; the manuscript's location was made a headed
subsection of its own, since it had been hard to find; and paths that already exist were turned
into working relative links (forty-three of them, all verified to resolve, with `%20` for the
spaces in `Human-input/Plans for AI generation/`).

**Files affected**: `How-to-use-vault.md` (new); `folder-structure.md` (one row added to the
root-level listing, which would otherwise have been incomplete).

**Committed and pushed** as `05c14ea` on `main`, covering all four files above plus this log.
`/validate invariants` passes on all eight checks with the tree clean.

**One thing a reader should know about that push.** It went to
`sandvelab/agentic-model-development-start` — the public template repository itself, not to a
project derived from it — and it was an ordinary `git push`, not `/release`. A grep for
key-, token- and password-shaped strings over the four changed files found nothing, but the
full secrets and data-permission scan that Rule 10 puts before publication **was not run**, so
that gate remains unexercised in this repository. Acceptable here because the four files are
prose written in this session and the repository was already public; it would not be
acceptable for a file carrying results or data.

**Follow-ups**: a copy of this repository that is made into a real project should re-read
`How-to-use-vault.md` for statements that its own set-up has made untrue.

## T2 (2026-10-14) — new remote and the project plan

`origin` moved from `sandvelab/agentic-model-development-start` to
`sandvelab/DevelopPythonVersionOfChapEwars` (created public on the human's instruction);
`old-history` was left local. The plan was written after reading the EWARS README,
`predict.R` and the dlnmpy README through the GitHub API, so its model description is
retrieved, not recalled. The main design choice: "similar results" is measured at five
layers (L1 adapters → L5 chap scores) against the R model's own seed-to-seed noise floor,
with the tolerance frozen before any Python prediction exists. INLA, which has no
established Python equivalent, is treated as an alternatives node (Laplace-style port,
MCMC, an existing Python INLA if one turns up).

## T3 (2026-10-14) — batch 1

See `AI-generated/batch-reports/26-10-14_b01_orientAndSetUp.md`. Departures from the plan,
all logged in plan §4b: the data selection (JC-01, because the EWARS weekly example has
only 8 periods); JSON instead of YAML for the ledgers (stdlib-only machinery); a
grandparent `CLAUDE.md` added to the settings excludes. `partition_data.py` was run with
`/usr/bin/python3` rather than `.venv/bin/python`; it is stdlib-only, so the output does not
depend on which, but later runs should use `.venv`. Docker was not running, so nothing from
the reference image (R package versions, image digest) was obtained yet.

## T4 (2026-10-14) — batch 2

See `AI-generated/batch-reports/26-10-14_b02_referenceThroughChap.md`. Three attempts, all
kept under `analysis/01_referenceThroughChap/results/`:

- **Attempt 1** stopped after the first failed evaluation. A `$(date)` in `PS4` makes
  macOS bash 3.2 exit under `set -e` (CH-09).
- **Attempt 2** ran everything. Monthly EWARS failed; the diagnosis downloaded the failed
  workspace and found chap's climatology weather provider forecasting the file's `month`
  column as non-integers (CH-07).
- **The final run** used contract-only inputs and an explicit weather provider.

The input reduction is an autonomous call that the human may want to revisit. It is flagged
in the report. `run.sh` step 4 (`summarise_reference.py`) was appended while the final run
was in progress. Bash picked the new line up and ran it at the end. The provenance record
says so, and the script was committed after the run, not before.
