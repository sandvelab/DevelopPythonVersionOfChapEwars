"""The R reference compared with itself, at L3, L4 and L5, as it runs (plan §4b, 2026-10-17).

Every fit and evaluation is kept. Each fit carries a health label (fidelity.health_label),
and each pair of runs is labelled by the health of its two members, so that the spread
between clean fits and the behaviour of flagged or crashed ones can be read side by side.

Inputs (03_referenceHarness/results): fit_summary.tsv; fits/<dataset>/<variant>/<run>/;
thread_diagnostic/ (single-threaded fits, kept as a separate set because they are not the
reference as it runs). L5: the per-row tables nc_to_rows.py wrote for every R evaluation.

Usage: describe_r_reference.py <harness results> <l5 rows dir> <out dir>
"""

import itertools
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from fidelity import (compare_chap_rows, compare_posterior, compare_predictive, health_label,
                      read_posterior, read_samples, summarise_posterior, summarise_predictive)

harness, l5dir, out = (Path(a) for a in sys.argv[1:4])
out.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- health of every fit
fs = pd.read_csv(harness / "fit_summary.tsv", sep="\t")
fs["crashed"] = fs["exit_code"] != 0
fs["health"] = [health_label(r.crashed, r.vb_correction_aborted, r.nconfig, r.n_theta, r.mode_status)
                for r in fs.itertuples()]
fs[["run_set", "dataset", "variant", "replicate", "health", "exit_code", "vb_correction_aborted",
    "nconfig", "n_theta", "mode_status", "theta_mode_1", "theta_mode_2", "theta_mode_3", "theta_mode_4",
    "fit_seconds"]].to_csv(out / "r_fit_health.tsv", sep="\t", index=False)
counts = (fs.groupby(["run_set", "dataset", "variant", "health"]).size()
          .unstack("health", fill_value=0).reset_index())
counts.to_csv(out / "r_fit_health_counts.tsv", sep="\t", index=False)


def future_periods(ds: str) -> set:
    return set(pd.read_csv(harness / "inputs" / ds / "future.csv")["time_period"].astype(str))


# ---------------------------------------------------------------- L3 and L4, all pairs
l3_rows, l4_rows, l3_detail, l4_detail = [], [], [], []
for run_set, root in (("fits", harness / "fits"), ("thread_diagnostic", harness / "thread_diagnostic")):
    sub = fs[fs["run_set"] == run_set]
    for (ds, var), runs in sub.groupby(["dataset", "variant"]):
        fut = future_periods(ds)
        ok = runs[~runs["crashed"]]
        post = {r.replicate: read_posterior(root / ds / var / r.replicate) for r in ok.itertuples()}
        samp = {r.replicate: read_samples(root / ds / var / r.replicate) for r in ok.itertuples()}
        health = dict(zip(runs["replicate"], runs["health"]))
        for a, b in itertools.combinations(sorted(post), 2):
            pair = {"run_set": run_set, "dataset": ds, "variant": var, "run_a": a, "run_b": b,
                    "pair_health": "+".join(sorted((health[a], health[b])))}
            m3 = compare_posterior(post[a], post[b])
            l3_detail.append(m3.assign(**pair))
            for s in summarise_posterior(m3).to_dict("records"):
                l3_rows.append({**pair, **s})
            m4 = compare_predictive(samp[a], samp[b])
            l4_detail.append(m4.assign(**pair))
            for s in summarise_predictive(m4, fut).to_dict("records"):
                l4_rows.append({**pair, **s})

pd.DataFrame(l3_rows).to_csv(out / "l3_r_vs_r_pairs.tsv", sep="\t", index=False)
pd.DataFrame(l4_rows).to_csv(out / "l4_r_vs_r_pairs.tsv", sep="\t", index=False)
pd.concat(l3_detail).to_csv(out / "l3_r_vs_r_quantities.tsv.gz", sep="\t", index=False)
pd.concat(l4_detail).to_csv(out / "l4_r_vs_r_rows.tsv.gz", sep="\t", index=False)

# ---------------------------------------------------------------- L5, all pairs of evaluations
l5 = {}
for f in sorted(l5dir.glob("*.tsv")):
    ds, model, run = f.stem.split("__")
    l5[(ds, model, run)] = pd.read_csv(f, sep="\t")
l5_rows = []
for ds in sorted({k[0] for k in l5}):
    runs = sorted(k for k in l5 if k[0] == ds and k[1] == "ewars_r")
    for a, b in itertools.combinations(runs, 2):
        l5_rows.append({"dataset": ds, "run_a": a[2], "run_b": b[2], **compare_chap_rows(l5[a], l5[b])})
    # the R original against each baseline, to put the spread in proportion
    for base in sorted(k for k in l5 if k[0] == ds and k[1] != "ewars_r"):
        for a in runs:
            l5_rows.append({"dataset": ds, "run_a": a[2], "run_b": f"{base[1]}", **compare_chap_rows(l5[a], l5[base])})
pd.DataFrame(l5_rows).to_csv(out / "l5_r_vs_r_pairs.tsv", sep="\t", index=False)
agg = pd.DataFrame([{"dataset": k[0], "model": k[1], "run": k[2], "status": "completed", "n_rows": len(v),
                     "mean_crps": v["crps"].mean()} for k, v in l5.items()])
# evaluations that produced no file: the chap repeats' exit codes (03_referenceHarness)
tm = pd.read_csv(harness / "chap_repeats" / "timings.tsv", sep="\t")
crashed = [{"dataset": r.dataset, "model": "ewars_r", "run": r.repeat, "status": "crashed", "n_rows": 0,
            "mean_crps": np.nan} for r in tm.itertuples() if r.exit_code != 0]
agg = pd.concat([agg, pd.DataFrame(crashed)], ignore_index=True)
agg.to_csv(out / "l5_evaluations.tsv", sep="\t", index=False)
print(counts.to_string())
print(pd.DataFrame(l3_rows).groupby(["run_set", "dataset", "variant", "pair_health", "group"])
      [["median_abs_z", "max_abs_z"]].median().to_string())
