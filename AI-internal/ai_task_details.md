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

## T5 (2026-10-14) — batch 3

See `AI-generated/batch-reports/26-10-14_b03_translationInventory.md`.
- **Records written before commit, then corrected.** I first wrote INLA's licence into
  `Archive/r-sources/provenance.md` as GPL; the installed DESCRIPTION and the repository's
  LICENSE say MIT. I corrected the file before it was committed.
- **Web fetch failed.** PyPI's web pages failed to load through the fetch tool, so the
  assessment uses PyPI's JSON API and pylgm's archived sdist instead.
- **The mapping is a judgment.** The parser output is mechanical, but the Python column and
  notes of `call_mapping.tsv` are mine.
- **Line endings in the archive (commit 83bad6b).** Git normalised CRLF line endings in
  the newly archived dlnm, r-inla and pylgm files when batch 3 was committed (00e8d63).
  A fresh checkout would then have failed their `sha256sums.txt`. `Archive/** -text` in
  `.gitattributes`, plus re-adding the two folders, fixed it. A fresh clone now verifies
  the manifests of all seven archive folders (batch 1's included, which were unaffected).
  The batch-2 workspace CSVs under `analysis/**/*workspace/` already had the same rule.

## T6 (2026-10-15) — batch 4

See `AI-generated/batch-reports/26-10-15_b04_referenceHarness.md` and
`analysis/03_referenceHarness/claim.md`.
- **What did not go to plan.** The seeded repeat was meant to show that a seeded run
  reproduces bit for bit. Its INLA fit differed instead: in the monthly case it reached a
  degenerate mode, while INLA reported success. A single-thread diagnostic was added to test
  threading as the cause. It did not explain the differences: single-threaded weekly fits
  crashed or degenerated too. One monthly chap repeat crashed in INLA. The sampler's own
  seeded reproducibility therefore remains untested in isolation (JC-15). A follow-up would
  draw twice from one saved fit.
- **Files written after the "before" commit.** `run_thread_diagnostic.sh`,
  `instrument_single_thread.R` and the summariser extension were written while the sweep ran,
  and committed at the contents they ran with (eb47134). Each provenance record says so.
- **Host sleep.** The Mac slept during the sweep, so wall-clock timings are upper bounds
  (CH-21). `run.sh` now uses `caffeinate -i`; the sweep itself did not.
- **Storage.** 168 MB of results. The per-row files of replicates 2–5 are gitignored, with a
  sha256 manifest (JC-18). Because of CH-20, a re-run does not regenerate them bit for bit.
- **Follow-ups.**
  - The human chooses how degenerate R fits enter the noise floor before batch 5 (report,
    "For the human").
  - Optionally, test on native amd64 whether emulation causes CH-20.

## T7 (2026-10-17) — batches 5–8 (candidate a) and 11

- **The human's decisions** (plan §4b, 2026-10-17): no tolerance file and no pass/fail; R's
  degenerate fits and crashes counted, not excluded; a runnable chap-compatible Python model
  with a short guide. Batches ran 5, 6, 7, 8 (candidate a only), 11; candidate (b) is open.
- **Nodes.** `04_fidelityMetrics` (measures, R-vs-R), `05_pythonModel` (package; children
  data layer, primitives, `03_inference/a_laplaceCcd`, `04_throughChap`), `06_closenessReport`.
  Every node imports the one package, so the code tested is the code served (JC-20).
- **The engine.** A subagent wrote a source-cited spec of INLA's compact mode
  (`a_laplaceCcd/results/inla_spec.md`). Details that mattered: 1e-4 added to the RW1 diagonal,
  the (N−r)/2·θ prior normalisation, configs sampled by density × CCD weight, and the
  VB-corrected sampling mean; `strategy='adaptive'` and `skew.corr` do nothing in compact
  mode. Departures are in JC-28.
- **What went wrong and was fixed.** The first R-vs-R comparison matched replicated random
  effects on ID and paired all years with each other (CH-24). pandas' default float parser
  was off by up to 3.7e-9 (CH-25). Two claims were drafted too strongly and were corrected
  before committing: monthly Python CRPS overlaps R's range, it is not inside it; and the
  objective-match figure is 0.021, not 0.016 (JC-31).
- **Follow-ups.** Candidate (b) (MCMC); phase D, whose budget can now use the measured costs;
  the holdout. On monthly data EWARS (R and Python alike) scores worse than seasonal_median
  and persistence, which is a finding about the model rather than the translation.

## T8 (2026-10-19) — batch 9, candidate (b): in progress

- **What exists.** Node `b_mcmcNuts` (an alternative; `a_laplaceCcd` stays the main path).
  `scripts/mcmc_nuts.py` writes the model in NumPyro so that its joint density is exactly the
  one `ewars_python.laplace` approximates, including INLA's normalising-constant convention;
  `check_target.py` verifies this (spread of the difference across 20 random points ≤ 4.4e-9).
  `run_mcmc_fits.py` writes the same files as the R harness and candidate (a), plus draws and
  convergence diagnostics; `compare.py` gives L3–L4 against R, MCMC-vs-MCMC and MCMC-vs-(a).
- **What did not work.** Non-centred iid effects mixed slowly (ESS 100 for τ_u); a dense mass
  matrix failed to adapt in 500 warm-up iterations (R-hat 2.2); 50 warm-up iterations left
  chains unconverged and overflowed the NB sampler. Centred iid effects with a diagonal mass
  matrix mixed well on monthly data but not on weekly (short test runs, scratchpad only, not
  results): min ESS 14–50, R-hat up to 1.21, up to 15 min for 450 iterations.
- **Being tested.** On the agent's diagnosis (unverified) of a ridge between intercept and the
  mean iid effect, a "split" parametrisation (level a = b0 + ū, deviations w, ū prior-only),
  verified to give the same density. The earlier "centred" version stays selectable.
- **The human's guidance** (2026-10-19, to go into plan §4b as human-set): try the
  reparametrisation, then decide the run length; small MCMC-vs-INLA differences are fine, only
  differences large enough to give very different results matter. So the full run needs to
  resolve substantial differences, not 0.01-sd ones.
- **Follow-ups.** Decide run length from the timing test; full run; commit after run; JC-32–34
  (engine/library, parametrisation and settings, main-path decision) and any CH entries for
  the mixing; claim.md answers; plan §4b and §6; batch report; re-render the translation record.

### T8, continued (2026-10-20) — batch 9 completed

- **The split parametrisation worked.** In the same short tests, weekly no_covariates went from
  879 s / min ESS 17 to 21 s / 221, and no tree-depth limit was hit. The full run (3 runs x 8
  variants, 4 x (1000 + 1000)) took 1.9 h: max R-hat 1.032, min ESS 179, 1 divergence.
- **Findings** (`b_mcmcNuts/results/summary_*.tsv`): the latent field and the forecasts agree
  with (a) and R within the MCMC's own run-to-run noise. Hyperparameter precisions are lower
  under MCMC (24 of 26 against (a)), by 0.03-0.07 sd and at most 0.16 sd. By the human's
  criterion this is small. (a) stays the main path (JC-34); (b) is kept runnable, not run through chap.
- **Anomaly kept on record.** One fit took 1999 s against 300-380 s for its siblings, with no
  sampler-side cause; most likely host sleep (cf. CH-21), noted in `provenance/mcmc_fits.md`.
- **Follow-ups.** Phase D (stability manifest and budget, with the human); phase E (holdout).
  JC-32 and JC-33 carry "matters: open", which JC-34 answers ("no"); the ledger is append-only.
