"""Tabulate what the harness runs recorded. Values are read from the run files and copied
or compared; no fidelity metric is computed here (that is batch 5's node).

Writes to <results_dir>:
  fit_summary.tsv        one row per instrumented fit: exit code, seconds, what INLA resolved
                         (nconfig, mode status, threads), sizes, and the CH-19 offset residual
  refit_agreement.tsv    per dataset x variant: the largest absolute difference of each L1-L3
                         output between replicate 1 and replicates 2-5 (seeded refits: the
                         fit takes no seed, so any difference is the engine's own), and
                         whether the L4 draws differ (they must, the seeds differ)
  thread_diagnostic.tsv  CH-20: the single-threaded fits (thread_diagnostic/) compared, file
                         by file; fit_summary.tsv also carries their rows (run_set)
  seeded_repeat.tsv      replicate 1 against its repeat with the same seeds, file by file:
                         identical content or the largest absolute difference
  chap_repeats.tsv       chap's metrics for every repeated chap evaluation, with its time
  fits_manifest.sha256   sha256 of every file under fits/ and thread_diagnostic/ (some are not in git; see claim.md)

Usage: summarise_harness.py <results_dir>
"""

import gzip
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

res = Path(sys.argv[1])
fits = res / "fits"
timings = pd.read_csv(fits / "timings.tsv", sep="\t")


def read_bytes(p: Path) -> bytes:
    return gzip.decompress(p.read_bytes()) if p.suffix == ".gz" else p.read_bytes()


def max_abs_diff(a: Path, b: Path) -> float:
    """Largest absolute difference over the numeric columns of two CSVs of equal shape."""
    x, y = pd.read_csv(a), pd.read_csv(b)
    if list(x.columns) != list(y.columns) or len(x) != len(y):
        return float("inf")
    num = [c for c in x.columns if pd.api.types.is_numeric_dtype(x[c])]
    if not num:
        return 0.0 if x.equals(y) else float("inf")
    d = np.abs(x[num].to_numpy(float) - y[num].to_numpy(float))
    nan_mismatch = np.isnan(x[num].to_numpy(float)) != np.isnan(y[num].to_numpy(float))
    if nan_mismatch.any():
        return float("inf")
    return float(np.nanmax(d)) if d.size else 0.0


# 1. fit_summary.tsv (the sweep, then the single-thread diagnostic if it ran)
diag = res / "thread_diagnostic"
runs = [(fits, t) for _, t in timings.iterrows()]
if (diag / "timings.tsv").exists():
    runs += [(diag, t) for _, t in pd.read_csv(diag / "timings.tsv", sep="\t").iterrows()]
rows = []
for base_dir, t in runs:
    d = base_dir / t["dataset"] / t["variant"] / t["replicate"]
    row = {"run_set": base_dir.name, **dict(t)}
    fi = d / "fit_info.json"
    if fi.exists():
        info = json.loads(fi.read_text())
        off = pd.read_csv(d / "offset_check.csv.gz")
        pred = pd.read_csv(d / "predictions.csv.gz", usecols=[0, 1])
        fixed = pd.read_csv(d / "fixed.csv")
        log = (d / "run.log").read_text(errors="replace")
        row.update(
            vb_correction_aborted=log.count("'vb.correction' is aborted"),
            **{f"theta_mode_{i + 1}": th for i, th in enumerate(info["theta_mode"])},
            nconfig=info["nconfig"], n_theta=len(info["theta_mode"]), mode_status=info["mode_status"],
            num_threads_fit=info["num_threads_fit"], inla_mode=info["inla_mode"],
            int_strategy=info["int_strategy"], fit_seconds=round(info["fit_elapsed_seconds"], 1),
            n_rows=info["n_rows"], n_predicted_rows=len(pred), n_fixed=len(fixed),
            offset_residual_max_abs=float(off["residual"].abs().max()),
        )
    rows.append(row)
pd.DataFrame(rows).to_csv(res / "fit_summary.tsv", sep="\t", index=False)

# 2. refit_agreement.tsv
L13 = ["model_frame.csv.gz", "fixed.csv", "hyperpar.csv", "configs.csv",
       "linear_predictor.csv.gz", "fitted_values.csv.gz"]
rows = []
for ds_dir in sorted(p for p in fits.iterdir() if p.is_dir()):
    for v_dir in sorted(p for p in ds_dir.iterdir() if p.is_dir()):
        base = v_dir / "rep1"
        reps = sorted(p for p in v_dir.iterdir() if p.name.startswith("rep") and p.name[3:].isdigit() and p.name != "rep1")
        if not (base / "fit_info.json").exists():
            continue
        randoms = sorted(f.name for f in base.glob("random_*.csv"))
        row = {"dataset": ds_dir.name, "variant": v_dir.name, "replicates_compared": len(reps) + 1}
        for f in L13 + randoms:
            diffs = [max_abs_diff(base / f, r / f) for r in reps if (r / f).exists()]
            row[f"{f}_max_abs_diff"] = max(diffs) if diffs else None
        row["l4_draws_differ_between_all_replicates"] = all(
            read_bytes(base / "posterior_draws.csv.gz") != read_bytes(r / "posterior_draws.csv.gz") for r in reps)
        rows.append(row)
pd.DataFrame(rows).to_csv(res / "refit_agreement.tsv", sep="\t", index=False)

# 3. seeded_repeat.tsv
rows = []
for ds_dir in sorted(p for p in fits.iterdir() if p.is_dir()):
    a, b = ds_dir / "default" / "rep1", ds_dir / "default" / "rep1_repeat"
    if not (a.exists() and b.exists()):
        continue
    for f in sorted(p.name for p in a.iterdir() if p.name != "run.log"):
        same = read_bytes(a / f) == read_bytes(b / f)
        diff = 0.0 if same else (max_abs_diff(a / f, b / f) if ".csv" in f else None)
        rows.append({"dataset": ds_dir.name, "file": f, "identical_content": same, "max_abs_diff": diff})
pd.DataFrame(rows).to_csv(res / "seeded_repeat.tsv", sep="\t", index=False)

# 3b. thread_diagnostic.tsv: single-threaded runs 2 and 3 against run 1, file by file
rows = []
if diag.exists():
    for ds_dir in sorted(p for p in diag.iterdir() if p.is_dir()):
        a = ds_dir / "default" / "single_thread_run1"
        for k in (2, 3):
            b = ds_dir / "default" / f"single_thread_run{k}"
            if not ((a / "fit_info.json").exists() and (b / "fit_info.json").exists()):
                continue
            for f in sorted(p.name for p in a.iterdir() if p.name not in ("run.log", "fit_info.json")):
                same = read_bytes(a / f) == read_bytes(b / f)
                diff = 0.0 if same else (max_abs_diff(a / f, b / f) if ".csv" in f else None)
                rows.append({"dataset": ds_dir.name, "compared": f"run1 vs run{k}", "file": f,
                             "identical_content": same, "max_abs_diff": diff})
    pd.DataFrame(rows).to_csv(res / "thread_diagnostic.tsv", sep="\t", index=False)

# 4. chap_repeats.tsv
cr = res / "chap_repeats"
if (cr / "timings.tsv").exists():
    tim = pd.read_csv(cr / "timings.tsv", sep="\t")
    rows = []
    for f in sorted((cr / "metrics").glob("*_metrics.csv")):
        m = pd.read_csv(f)
        for _, r in m.iterrows():
            stem = Path(r["filename"]).stem  # <dataset>__ewars_r__repN
            ds, _, rep = stem.split("__")
            t = tim[(tim["dataset"] == ds) & (tim["repeat"] == rep)]
            rows.append({"dataset": ds, "repeat": rep, "crps": r["crps"], "crps_log1p": r["crps_log1p"],
                         "mae": r["mae"], "coverage_10_90": r["coverage_10_90"],
                         "coverage_25_75": r["coverage_25_75"],
                         "seconds": int(t["seconds"].iloc[0]) if len(t) else None})
    pd.DataFrame(rows).sort_values(["dataset", "repeat"]).to_csv(res / "chap_repeats.tsv", sep="\t", index=False)

# 5. fits_manifest.sha256
with open(res / "fits_manifest.sha256", "w") as out:
    for p in sorted(list(fits.rglob("*")) + (list(diag.rglob("*")) if diag.exists() else [])):
        if p.is_file():
            out.write(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(res)}\n")

print((res / "fit_summary.tsv").read_text())
