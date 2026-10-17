"""The closeness report: the Python model beside the R reference, layer by layer, with the
R reference's own run-to-run behaviour as it runs set beside it. No pass/fail (plan §4b,
2026-10-17); every number is read from the files the nodes wrote, and the table each one
comes from is named under it.

Usage: build_closeness_report.py <analysis dir> <out dir>
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

A, out = Path(sys.argv[1]), Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
N04 = A / "04_fidelityMetrics/results"
N51 = A / "05_pythonModel/01_dataLayer/results"
N52 = A / "05_pythonModel/02_modelPrimitives/results"
N53 = A / "05_pythonModel/03_inference/a_laplaceCcd/results"
N54 = A / "05_pythonModel/04_throughChap/results"


def tsv(p):
    return pd.read_csv(p, sep="\t")


def rng(s: pd.Series, fmt="{:.3f}") -> str:
    s = s.dropna()
    if len(s) == 0:
        return "–"
    lo, hi = s.min(), s.max()
    return fmt.format(lo) if np.isclose(lo, hi) else f"{fmt.format(lo)} – {fmt.format(hi)}"


def md(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    lines += ["| " + " | ".join(str(v) for v in row) + " |" for row in df.itertuples(index=False)]
    return "\n".join(lines)


L = []
L.append("# How close the Python EWARS model is to the R original\n")
L.append("The Python model (`analysis/05_pythonModel/scripts/chapkit_ewars_python/`) is set beside the "
         "R original (`chapkit_ewars_model` @ 964eea8b, R-INLA 25.10.19) at five layers, on the two "
         "development datasets: monthly EWARS example (23 locations) and weekly Nicaragua (10 locations). "
         "At each layer the same measures are also given for the R original against itself, with nothing "
         "changed between runs, so that the reader can judge the Python–R distance against the R–R "
         "distance. Nothing is excluded: every R fit is labelled *clean*, *flagged* or *crashed* "
         "(04_fidelityMetrics), and pairs involving a flagged R fit are shown separately.\n")

# ---------------------------------------------------------------- R behaviour
hc = tsv(N04 / "r_fit_health_counts.tsv")
for c in ("clean", "flagged", "crashed"):
    if c not in hc:
        hc[c] = 0
ev = tsv(N04 / "l5_evaluations.tsv")
evr = ev[ev["model"] == "ewars_r"]
L.append("## The R original's own behaviour\n")
L.append("Seeded refits on identical inputs (2 datasets × 4 config variants, 5 replicates plus one "
         "seeded repeat of the default), and single-threaded diagnostic fits:\n")
L.append(md(hc[["run_set", "dataset", "variant", "clean", "flagged", "crashed"]]))
L.append("\n*Source: `04_fidelityMetrics/results/r_fit_health_counts.tsv`. Flagged: a logged VB-correction "
         "abort, a non-zero mode status, or fewer than half the integration points.*\n")
evc = evr.groupby(["dataset", "status"]).size().unstack(fill_value=0).reset_index()
L.append("Evaluations of the R original through chap (batch 2's run plus the repeats):\n")
L.append(md(evc))
L.append("\n*Source: `04_fidelityMetrics/results/l5_evaluations.tsv`. A crashed evaluation produced no "
         "scores: INLA stopped in one backtest split.*\n")

# ---------------------------------------------------------------- L1-L2
l12 = tsv(N51 / "l1_l2_comparison.tsv")
L.append("## L1–L2: model frame and cross-basis\n")
t = l12[["dataset", "variant", "frame_max_abs_diff", "basis_max_abs_diff", "string_mismatches",
         "na_pattern_mismatches"]].copy()
t["frame_max_abs_diff"] = t["frame_max_abs_diff"].map("{:.1e}".format)
t["basis_max_abs_diff"] = t["basis_max_abs_diff"].map("{:.1e}".format)
L.append(md(t))
L.append("\n*Source: `05_pythonModel/01_dataLayer/results/l1_l2_comparison.tsv`. Python against the "
         "frame and cross-basis the R reference built from the same files. The R side is identical "
         "across all its refits (03_referenceHarness), so the R–R distance here is 0.*\n")

# ---------------------------------------------------------------- objective
pc = tsv(N52 / "primitives_check.tsv")
ob = tsv(N53 / "objective_at_inla_configs.tsv")
ob["absd"] = ob["diff"].abs()
fh_all = tsv(N04 / "r_fit_health.tsv")
fh_all = fh_all[fh_all["run_set"] == "fits"].rename(columns={"replicate": "r_run"})
ob = ob.merge(fh_all[["dataset", "variant", "r_run", "health"]], on=["dataset", "variant", "r_run"], how="left")
obs = (ob.groupby(["dataset", "variant", "health"])["absd"].max().unstack("health").reset_index())
L.append("## The model pieces and the fitted objective\n")
pcs = pc.groupby("quantity")["abs_or_rel_diff"].max().reset_index()
pcs["abs_or_rel_diff"] = pcs["abs_or_rel_diff"].map("{:.1e}".format)
L.append(md(pcs.rename(columns={"abs_or_rel_diff": "max difference from INLA / R"})))
L.append("\n*Source: `05_pythonModel/02_modelPrimitives/results/primitives_check.tsv` (scale factor: relative; "
         "the rest absolute).*\n")
L.append("The Python Laplace log posterior of the hyperparameters, evaluated at INLA's own integration "
         "points of every R fit, against the relative log posterior INLA recorded there (log units):\n")
for c in ("clean", "flagged"):
    if c in obs:
        obs[c] = obs[c].map(lambda v: "–" if v != v else f"{v:.4f}")
obs = obs.rename(columns={"clean": "max |difference|, clean R fits", "flagged": "max |difference|, flagged R fit"})
L.append(md(obs))
L.append("\n*Source: `05_pythonModel/03_inference/a_laplaceCcd/results/objective_at_inla_configs.tsv`, with "
         "each R fit's health from `04_fidelityMetrics/results/r_fit_health.tsv`. At the flagged fit's "
         "points the two objectives disagree by thousands of log units: INLA's recorded values there "
         "come from a degenerate fit.*\n")

# ---------------------------------------------------------------- L3
p3 = tsv(N53 / "l3_python_vs_r_pairs.tsv")
r3 = tsv(N04 / "l3_r_vs_r_pairs.tsv")
r3 = r3[r3["run_set"] == "fits"]
L.append("## L3: posterior\n")
L.append("Shift in posterior mean, in pooled posterior sds, per quantity; the cells give the range over "
         "pairs of the per-pair median |shift| (max |shift| in brackets). Groups: hyperparameters (NB "
         "size and precisions), fixed effects (intercept and cross-basis coefficients), random effects "
         "(all values of all terms).\n")
rows3 = []
for (ds, var), g in r3.groupby(["dataset", "variant"]):
    for grp, label in (("hyperparameter", "hyperparameters"), ("fixed", "fixed effects"), ("random", "random effects")):
        sel = (lambda d: d["group"].str.startswith("random")) if grp == "random" else (lambda d: d["group"] == grp)
        rr = g[sel(g) & (g["pair_health"] == "clean+clean")]
        rf = g[sel(g) & (g["pair_health"] != "clean+clean")]
        pp = p3[(p3.dataset == ds) & (p3.variant == var) & (p3.comparison == "python_vs_r")]
        pc_ = pp[sel(pp) & (pp["r_health"] == "clean")]
        pf = pp[sel(pp) & (pp["r_health"] != "clean")]
        rows3.append({"dataset": ds, "variant": var, "quantities": label,
                      "R vs R, clean pairs": f"{rng(rr['median_abs_z'])} ({rng(rr['max_abs_z'], '{:.2f}')})",
                      "Python vs R, clean R": f"{rng(pc_['median_abs_z'])} ({rng(pc_['max_abs_z'], '{:.2f}')})",
                      "R vs R, a flagged fit": f"{rng(rf['median_abs_z'], '{:.1f}')}" if len(rf) else "–",
                      "Python vs R, flagged R": f"{rng(pf['median_abs_z'], '{:.1f}')}" if len(pf) else "–"})
t3 = pd.DataFrame(rows3)
t3.to_csv(out / "l3_table.tsv", sep="\t", index=False)
L.append(md(t3))
L.append("\n*Sources: `04_fidelityMetrics/results/l3_r_vs_r_pairs.tsv`, "
         "`05_pythonModel/03_inference/a_laplaceCcd/results/l3_python_vs_r_pairs.tsv`. Python: 3 runs "
         "per variant (the fit is deterministic; runs differ by sampler seed), each against each R run.*\n")

# hyperparameter modes
fh = tsv(N04 / "r_fit_health.tsv")
fh = fh[fh["run_set"] == "fits"]
import json  # noqa: E402
mrows = []
for (ds, var), g in fh.groupby(["dataset", "variant"]):
    info = json.loads((N53 / "python_fits/fits" / ds / var / "rep1" / "fit_info.json").read_text())
    cl = g[g["health"] == "clean"]
    for k in range(1, 5):
        col = f"theta_mode_{k}"
        if col not in g or g[col].isna().all():
            continue
        mrows.append({"dataset": ds, "variant": var, "theta": ["log size", "log prec iid", "log prec RW1",
                                                                 "log prec RW1 by location"][k - 1],
                      "R clean fits (range)": rng(cl[col]), "Python": f"{info['theta_mode'][k - 1]:.3f}",
                      "R flagged fits": ", ".join(f"{v:.2f}" for v in g[g["health"] == "flagged"][col]) or "–"})
tm = pd.DataFrame(mrows)
tm.to_csv(out / "theta_mode_table.tsv", sep="\t", index=False)
L.append("Where the hyperparameter mode lands (INLA's internal scale):\n")
L.append(md(tm))
L.append("\n*Sources: `04_fidelityMetrics/results/r_fit_health.tsv`; "
         "`05_pythonModel/03_inference/a_laplaceCcd/results/python_fits/fits/*/*/rep1/fit_info.json`.*\n")

# ---------------------------------------------------------------- L4
p4 = tsv(N53 / "l4_python_vs_r_pairs.tsv")
r4 = tsv(N04 / "l4_r_vs_r_pairs.tsv")
r4 = r4[(r4["run_set"] == "fits") & (r4["rows"] == "forecast_rows")]
p4 = p4[p4["rows"] == "forecast_rows"]
L.append("## L4: predictive samples (forecast rows)\n")
L.append("Per forecast row, from the 1000 samples: the shift in predictive mean in pooled predictive sds, "
         "and the Wasserstein-1 distance between the two sample sets in pooled sds; cells give the median "
         "over pairs of the per-pair median. With 1000 samples, Monte Carlo error alone gives about 0.03 "
         "and 0.05; the Python–Python column (sampler seed only) shows that floor directly. The 90 % "
         "interval-width ratio is the median over pairs of the per-pair median.\n")
rows4 = []
for (ds, var), g in r4.groupby(["dataset", "variant"]):
    rr = g[g["pair_health"] == "clean+clean"]
    rf = g[g["pair_health"] != "clean+clean"]
    pp = p4[(p4.dataset == ds) & (p4.variant == var)]
    pc_ = pp[(pp.comparison == "python_vs_r") & (pp.r_health == "clean")]
    pf = pp[(pp.comparison == "python_vs_r") & (pp.r_health != "clean")]
    py = pp[pp.comparison == "python_vs_python"]

    def cell(d):
        if len(d) == 0:
            return "–"
        return (f"{d['median_abs_z_mean_shift'].median():.3f} / {d['median_abs_w1_over_sd'].median():.3f} / "
                f"{d['width90_ratio_median'].median():.2f}")
    rows4.append({"dataset": ds, "variant": var, "R vs R, clean": cell(rr), "Python vs R, clean R": cell(pc_),
                  "Python vs Python": cell(py), "pairs with a flagged R fit": cell(pd.concat([rf.assign(), pf]))})
t4 = pd.DataFrame(rows4)
t4.to_csv(out / "l4_table.tsv", sep="\t", index=False)
L.append(md(t4))
L.append("\n*Cells: mean shift / W1 / width ratio. Sources: `04_fidelityMetrics/results/l4_r_vs_r_pairs.tsv`, "
         "`05_pythonModel/03_inference/a_laplaceCcd/results/l4_python_vs_r_pairs.tsv`.*\n")

# ---------------------------------------------------------------- L5
L.append("## L5: chap's backtest scores\n")
p5e = tsv(N54 / "l5_evaluations.tsv")
p5 = tsv(N54 / "l5_pairs.tsv")
rows5 = []
for ds, g in p5e.groupby("dataset"):
    r_runs = g[g.model == "ewars_r"]["mean_crps"]
    py_runs = g[g.model == "ewars_python"]["mean_crps"]
    n_crash = int(((evr.dataset == ds) & (evr.status == "crashed")).sum())
    row = {"dataset": ds,
           "R original (CRPS per run)": ", ".join(f"{v:.2f}" for v in sorted(r_runs)) + (f"; {n_crash} crashed" if n_crash else ""),
           "Python (CRPS per run)": ", ".join(f"{v:.2f}" for v in sorted(py_runs))}
    for b in ("seasonal_median", "persistence", "global_median"):
        v = g[g.model == b]["mean_crps"]
        row[b] = f"{v.iloc[0]:.2f}" if len(v) else "–"
    rows5.append(row)
t5 = pd.DataFrame(rows5)
t5.to_csv(out / "l5_table.tsv", sep="\t", index=False)
L.append("Aggregate CRPS (lower is better), each run of each model, and chap's baselines:\n")
L.append(md(t5))
L.append("\nPaired per-row differences in CRPS (each row a location × forecast period × horizon), "
         "median over pairs of runs:\n")
s5 = (p5[p5.comparison.isin(["r_vs_r", "python_vs_r", "python_vs_python"])]
      .groupby(["dataset", "comparison"])[["mean_diff", "median_abs_diff", "mean_abs_diff"]].median().reset_index())
base = (p5[p5.comparison.str.startswith("python_vs_") & ~p5.comparison.isin(["python_vs_r", "python_vs_python"])]
        .groupby(["dataset", "comparison"])[["mean_diff", "median_abs_diff", "mean_abs_diff"]].median().reset_index())
s5 = pd.concat([s5, base], ignore_index=True)
for c in ("mean_diff", "median_abs_diff", "mean_abs_diff"):
    s5[c] = s5[c].map("{:.3f}".format)
s5.to_csv(out / "l5_pairs_table.tsv", sep="\t", index=False)
L.append(md(s5))
L.append("\n*mean_diff: second minus first, so negative favours the second. Sources: "
         "`05_pythonModel/04_throughChap/results/l5_evaluations.tsv`, `l5_pairs.tsv`; the R evaluations "
         "from `04_fidelityMetrics/results/l5_rows/`.*\n")

L.append("## Reading this report\n")
L.append("No threshold is applied. For each layer, compare the *Python vs R, clean R* column with the "
         "*R vs R, clean* column, and the flagged columns with each other, to judge whether the Python "
         "model is as close to the R original as the R original is to itself. The L5 baselines put the "
         "size of any Python–R gap in proportion.\n")
(out / "closeness_report.md").write_text("\n".join(L))
print("\n".join(L))
