"""Compare a clean-shell run of the tutorial with the reference run (run1).

Checks, each written as one PASS/FAIL line:
  1. the tutorial ran to the end (exit code 0);
  2. its monthly input is byte-identical to the reference run's monthly input;
  3. its seasonal_median scores equal the reference run's on every metric (the baseline is
     deterministic, so any difference means the two pipelines differ);
  4. its EWARS evaluation produced scores.
EWARS scores are not required to match: the R code is unseeded (CH-10). Both CRPS values are
printed, as a first look at the run-to-run variation the batch-4 noise floor measures.

Usage: compare_tutorial_run.py <tutorial_dir> <reference_run_dir> <tutorial_exit_code>
"""

import hashlib
import sys
from pathlib import Path

import pandas as pd

tut, ref, rc = Path(sys.argv[1]), Path(sys.argv[2]), int(sys.argv[3])
checks = []


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


checks.append(("tutorial ran to the end", rc == 0, f"exit code {rc}"))

a, b = tut / "monthly.csv", ref / "inputs" / "monthly_ewars.csv"
same = a.exists() and sha(a) == sha(b)
checks.append(("monthly input identical to run1", same, f"{sha(a)[:12] if a.exists() else 'missing'} vs {sha(b)[:12]}"))

tm = pd.read_csv(tut / "metrics.csv") if (tut / "metrics.csv").exists() else pd.DataFrame()
rm = pd.read_csv(ref / "metrics" / "monthly_ewars_metrics.csv")
metric_cols = [c for c in rm.columns if c not in ("filename", "model_name", "model_version")]


def row(df: pd.DataFrame, model: str):
    hit = df[df["model_name"] == model] if "model_name" in df else df
    return hit.iloc[0] if len(hit) == 1 else None


t_sm, r_sm = row(tm, "builtin:seasonal_median"), row(rm, "builtin:seasonal_median")
if t_sm is None or r_sm is None:
    checks.append(("seasonal_median scores equal run1", False, "row missing"))
else:
    diff = [c for c in metric_cols if not (t_sm[c] == r_sm[c] or (pd.isna(t_sm[c]) and pd.isna(r_sm[c])))]
    checks.append(("seasonal_median scores equal run1", not diff, f"differing metrics: {diff or 'none'}"))

t_ew = tm[tm["model_name"].astype(str).str.startswith("http")] if "model_name" in tm else tm
r_ew = rm[rm["model_name"].astype(str).str.startswith("http")]
ok = len(t_ew) == 1 and pd.notna(t_ew.iloc[0]["crps"])
checks.append(("EWARS evaluation produced scores", ok, f"{len(t_ew)} row(s)"))

for name, passed, detail in checks:
    print(f"{'PASS' if passed else 'FAIL'}  {name}  ({detail})")
if ok and len(r_ew) == 1:
    print(f"INFO  EWARS crps: tutorial run {t_ew.iloc[0]['crps']!r}, run1 {r_ew.iloc[0]['crps']!r}")
print("VERDICT", "PASS" if all(p for _, p, _ in checks) else "FAIL")
