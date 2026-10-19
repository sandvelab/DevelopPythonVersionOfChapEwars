"""The tables candidate (b)'s answers are read from.

  summary_l3.tsv            per dataset x variant x group: the median over pairs of each
                            pair's median |z| shift, for mcmc_vs_r (clean R fits),
                            mcmc_vs_laplace and mcmc_vs_mcmc
  summary_hyperparameters.tsv  per hyperparameter: the median signed shift and sd ratio
                            (b minus the other), same three comparisons
  summary_l4.tsv            forecast rows: median over pairs of the median |z| mean shift,
                            median W1 / pooled sd and median 90 % width ratio
  summary_cost.tsv          per dataset x variant: seconds, divergences, tree-depth hits,
                            min ESS and max R-hat over the runs, and candidate (a)'s seconds

Usage: summarise.py <b results dir> <a timings tsv>
"""

import sys
from pathlib import Path

import pandas as pd

res, a_tim = Path(sys.argv[1]), Path(sys.argv[2])
KEEP = ["clean", "-"]  # the flagged R fit is compared in compare.py's tables, not summarised here
COMP = ["mcmc_vs_r", "mcmc_vs_laplace", "mcmc_vs_mcmc"]

l3 = pd.read_csv(res / "l3_mcmc_pairs.tsv", sep="\t")
l3 = l3[l3["r_health"].isin(KEEP)]
s3 = (l3.groupby(["dataset", "variant", "group", "comparison"])["median_abs_z"].median()
      .unstack()[COMP].reset_index())
s3.to_csv(res / "summary_l3.tsv", sep="\t", index=False, float_format="%.4f")

q = pd.read_csv(res / "l3_mcmc_quantities.tsv.gz", sep="\t")
q = q[(q["group"] == "hyperparameter") & q["r_health"].isin(KEEP)]
sh = q.groupby(["dataset", "variant", "name", "comparison"])[["z_mean_shift", "sd_ratio"]].median().unstack()
sh.columns = [f"{m}:{c}" for m, c in sh.columns]
sh = sh[[f"{m}:{c}" for m in ["z_mean_shift", "sd_ratio"] for c in COMP]].reset_index()
sh.to_csv(res / "summary_hyperparameters.tsv", sep="\t", index=False, float_format="%.4f")

l4 = pd.read_csv(res / "l4_mcmc_pairs.tsv", sep="\t")
l4 = l4[(l4["rows"] == "forecast_rows") & l4["r_health"].isin(KEEP)]
s4 = (l4.groupby(["dataset", "variant", "comparison"])
      [["median_abs_z_mean_shift", "median_abs_w1_over_sd", "width90_ratio_median"]].median().reset_index())
s4.to_csv(res / "summary_l4.tsv", sep="\t", index=False, float_format="%.4f")

fits = pd.read_csv(res / "mcmc_fits" / "mcmc_fits_summary.tsv", sep="\t")
cost = fits.groupby(["dataset", "variant"]).agg(
    runs=("replicate", "count"), seconds_min=("seconds", "min"), seconds_max=("seconds", "max"),
    divergences=("divergences", "sum"), tree_depth_hits=("max_tree_depth_hits", "sum"),
    min_ess=("min_ess", "min"), max_rhat=("max_rhat", "max")).reset_index()
a = pd.read_csv(a_tim, sep="\t").groupby(["dataset", "variant"])["seconds"].agg(
    a_seconds_min="min", a_seconds_max="max").reset_index()
cost.merge(a, on=["dataset", "variant"]).to_csv(res / "summary_cost.tsv", sep="\t", index=False)

print(s3.round(3).to_string(), s4.round(3).to_string(), cost.to_string(), sep="\n\n")
print("\nall: max |median shift| per comparison, by group kind")
s3["kind"] = s3["group"].where(s3["group"] == "hyperparameter", "latent")
print(s3.groupby("kind")[COMP].agg(["min", "max"]).round(3).to_string())
print(s4[["comparison", "median_abs_z_mean_shift", "median_abs_w1_over_sd", "width90_ratio_median"]]
      .groupby("comparison").agg(["min", "max"]).round(3).to_string())
print(sh[["z_mean_shift:mcmc_vs_r", "z_mean_shift:mcmc_vs_laplace", "z_mean_shift:mcmc_vs_mcmc"]]
      .agg(["min", "max"]).round(3).to_string())
print("hyperparameters with negative shift vs laplace:", int((sh["z_mean_shift:mcmc_vs_laplace"] < 0).sum()),
      "of", len(sh))
