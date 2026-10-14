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
