# Task history

One line per completed task. Written by `/log-tasks`; expanded entries in
`ai_task_details.md`.

This log is **part of the published record** of how the work came about. Write entries a
reader who was not present can follow, and keep them honest about what did not work.

- T1 (2026-09-22): Wrote `How-to-use-vault.md`, a human-facing walkthrough of how this
  repository is used — set-up, fixing the anchors, the `/do` batch loop, the claim tree,
  which skill to use when, where the article and the results are found, and what each log
  records. Revised once on human feedback (see `ai_task_details.md`), then committed and
  pushed to `origin/main` as `05c14ea`. No analysis; the project is still undefined.
- T2 (2026-10-14): Repointed `origin` to the new public repository
  `sandvelab/DevelopPythonVersionOfChapEwars` and pushed `main`; wrote the project plan
  `26-10-14_pythonEwarsForChap.md` (Python port of CHAP-EWARS, run through chap).
- T3 (2026-10-14): Ran batch 1 of that plan: cloned and pinned chap-core, chapkit,
  chapkit_ewars_model and dlnmpy into `Archive/`; partitioned the data and sealed the holdout;
  started the judgment-call and challenge ledgers and their renderer; filled in
  `readme-at-start.md`. Blocked for batch 2 on Docker not running (CH-02).
- T4 (2026-10-14): Ran batch 2: the R original scored through chap-core on both development
  datasets with chap's three built-in baselines, from a fresh shell; tutorial written and
  verified by a clean-shell run of its own commands. The R original's monthly example failed
  inside INLA through chap (CH-07); diagnosed from the failed job's workspace and resolved by
  reducing inputs to the data contract (JC-05).
- T5 (2026-10-14): Ran batch 3: archived R-INLA 25.10.19 and dlnm 2.4.10 sources and the
  reference image's installed defaults; listed every R call with R's parser and mapped each
  to Python (none unmapped); assessed existing Python INLAs (none usable as candidate c);
  pinned the main environment. Then made `Archive/` byte-exact in git (`.gitattributes`), after
  git had normalised CRLF line endings in the new imports; every archive manifest verified on
  a fresh clone.
- T6 (2026-10-15): Batch 4, the R reference harness (`analysis/03_referenceHarness/`).
  - The archived `predict_chap` is instrumented by inserting taps into its parsed body; the
    only changed statement seeds the sampler.
  - 42 fits: 2 datasets × 4 variants × 5 seeded replicates, plus a seeded repeat. Each writes
    L1–L4 to file.
  - 4 unseeded chap repeats per dataset (L5), and a single-thread diagnostic.
  - Findings: L1/L2 are deterministic; INLA's Predictor includes log(E) (CH-19 resolved); the
    INLA fit is not reproducible on identical inputs and sometimes degenerates or crashes,
    single-threaded too (CH-20). Batch 5 is held for the human.
- T7 (2026-10-17): Batches 5–8 (candidate a) and 11, after the human's answer to CH-20: no
  pass/fail, a closeness report with the R reference counted as it runs, and a runnable model.
  - Built the Python EWARS model as a chapkit service
    (`analysis/05_pythonModel/scripts/chapkit_ewars_python/`, run guide in its README),
    following INLA's compact-mode engine from its archived C source (`Archive/r-inla-gmrflib/`).
  - Findings: L1 exact, L2 4.4e-16; L3–L4 inside the R refits' own spread; chap CRPS overlaps
    the R runs' range on both datasets. Report: `analysis/06_closenessReport/results/closeness_report.md`.
