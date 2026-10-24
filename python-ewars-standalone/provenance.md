# Provenance

One section per file or folder in `python-ewars-standalone/`, saying where it was copied
from. Append a section when `refresh.sh` is run again; never overwrite one.

## model/ (2026-10-21, commit 2ae1fef)

Copied by `refresh.sh` from `analysis/05_pythonModel/scripts/chapkit_ewars_python/`, the
Python model's source of truth, leaving out what a local run creates (`.venv/`,
`example_run/`, `data/`, `__pycache__/`). Its own `README.md` is the package's run guide and
refers to paths in the full repository. The model is the main-path candidate (a) of
`analysis/05_pythonModel/03_inference/`; its provenance records are in that tree.

## data/ (2026-10-21, commit 2ae1fef)

- `weekly_nicaragua.csv`, `monthly_ewars.csv`: copied from
  `analysis/01_referenceThroughChap/results/run1/inputs/`, the development datasets in the
  six-column form chap reads (JC-05), prepared by that node's `scripts/prepare_inputs.py`
  from `Archive/dev-data/`. Public example data; licence as stated in
  `Archive/dev-data/provenance.md` (CH-03).
- `weekly_nicaragua/`, `monthly_ewars/` (`historic.csv`, `future.csv`): copied from
  `analysis/03_referenceHarness/results/inputs/`, the same data as chap hands the model at
  its last backtest split, used by the harness for direct fits.

## config/ (2026-10-21, commit 2ae1fef)

- `ewars_config.yaml`: copied from `analysis/01_referenceThroughChap/scripts/`, the
  configuration both models were evaluated with through chap.
- `predict_config.yml`: written by `refresh.sh`; the same settings in the flat form
  `scripts/predict.py` reads.

## README.md, refresh.sh (2026-10-21)

Written by the agent on the human's request (plan §4b, 2026-10-21; ledger row 13). The
guide's commands follow the model's verified run guide, with relative paths and chap
installed as a uv tool at its current release instead of the pinned commit. The release's
`chap eval` and `chap export-metrics` options were checked against the pinned commit's on
2026-10-21 (chap-core 2.3.1 on PyPI; the project pinned 2.5.0.dev0 at `b8c8f788`).

## check/ (2026-10-21)

The guide's blocks, run from a copy of this folder placed outside the repository, with
`uvx --from chap-core chap` standing in for the installed tool so that nothing is installed
on the machine. `guide_run.log` is the full output; `guide_exit_code.txt` the exit status.
