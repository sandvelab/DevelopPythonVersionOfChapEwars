# Batch 1 — Orient and set up

Generated from [[26-10-14_pythonEwarsForChap]] — batch 1 (phase A). No modelling.

## What was done

- **The anchors were cloned and pinned.** `AI-internal/data-acquisition/fetch_repos.sh`
  cloned four repositories (log: `fetch_repos.log`). Each is archived as `Archive/<name>/src`
  with `.git` removed, plus `sha256sums.txt`, `README.md` and `provenance.md`:

  | Repository | Commit | Licence |
  |---|---|---|
  | chap-models/chapkit_ewars_model | `964eea8bfdb194ca8985723216e94f1ac63aa4f1` | GPL-3.0 |
  | dhis2-chap/chap-core | `b8c8f788fbc011f3d9d8a18ba9e993725023a6e4` | AGPL-3.0 |
  | dhis2-chap/chapkit | `b8ccd072cbf0d4c70fa34f8e818551ca5937aa75` | AGPL-3.0 |
  | Logic06183/dlnmpy | `8c5edd79ea989d22b457bfb93e03b0c5e125792c` | GPL-2.0 |

  The chap documentation is part of the chap-core clone (`src/docs/`, including
  `chap-cli/evaluation-workflow.md` and `chap-cli/eval-reference.md`, which batch 2 needs).
- **The plan's facts about the R model were re-verified** against the pinned
  `scripts/predict.R`:
  - the INLA formula (lines 59–65, 110–117);
  - the cross-basis specification (lines 85–95);
  - the `inla()` call with `control.fixed(prec.intercept = 1e-4, prec = precision)`
    (lines 192–195);
  - the sampling from `inla.posterior.sample` + `rnbinom(mu, size)` (lines 204–209).

  All of them match the plan's §1.
- **The data was partitioned and the holdout sealed** by
  `AI-internal/data-acquisition/partition_data.py` (log: `partition_data.log`). The
  selection used only file names, columns, row counts, location ids and period ranges:

  | Set | Content | Rows |
  |---|---|---|
  | dev, monthly | EWARS `example_data_monthly/` historic + future (23 locations, 2001-01..2017-06) | 4416 + 138 |
  | dev, weekly | chap-core Nicaragua weekly, periods before 2018-01-01 (10 locations) | 7310 |
  | dev, smoke | EWARS `example_data/` training + future (13 locations, 8 periods) | 104 + 52 |
  | holdout, monthly | chap-core `laos_subset.csv` (3 locations, 2010-01..2012-12) | 108 |
  | holdout, weekly | chap-core Nicaragua weekly in full; targets from 2018-01-01 | 9840 |

  This departs from the plan's default data choice, for the reason in JC-01 and CH-01. It
  is recorded in the plan's §4b.
- **The translation ledgers and their renderer exist.** The ledgers are
  `AI-internal/translation-log/{judgment_calls,challenges}.json`; the renderer is
  `AI-internal/useful-scripts/render_translation_record.py`; the rendered documents are
  `AI-generated/translation-record/{judgment-calls,challenges}.md`. They currently hold
  JC-01 and CH-01 to CH-06.
- **The set-up was finished.** The plan was archived to `Archive/plan-as-delivered/`. The
  `.claude/settings.json` placeholders were filled in. `readme-at-start.md` and
  `analysis/claim.md` were written from the plan.

## Open questions for the human

1. **Docker** (CH-02): the daemon was not running. Batch 2 needs Docker Desktop started,
   because the R reference image is amd64-only and runs under emulation on this Mac.
2. **Q1–Q3 in plan §4** still stand, with their defaults. Q1 is partly answered by the data
   selection above; the human may still prefer a real dataset as the holdout.

## Next

Batch 2: run the original EWARS through chap from a fresh shell, and write the tutorial
from the script that ran it.
