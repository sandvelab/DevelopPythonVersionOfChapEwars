"""Describing how close two runs of the EWARS model are, layer by layer (plan §2).

No pass/fail and no tolerance (plan §4b, 2026-10-17): every function returns
descriptive numbers, and the reader applies the yardstick. The same functions serve
R-vs-R (the reference's own run-to-run behaviour) and Python-vs-R.

A *run directory* holds the files the instrumented R reference writes per fit
(03_referenceHarness), and which the Python model writes in the same names:
  fit_info.json (exit status, theta_mode, nconfig, ...), hyperpar.csv, fixed.csv,
  random_<term>.csv (ID, mean, sd), predictions.csv.gz (time_period, location,
  sample_0..sample_999).

Measures, per pair of runs (a, b):
  L3  for every posterior quantity (hyperparameter, fixed effect, random-effect value):
      the shift in posterior mean in units of the pooled posterior sd,
      z = (mean_b - mean_a) / sqrt((sd_a^2 + sd_b^2) / 2), and the sd ratio sd_b / sd_a.
  L4  for every predicted row, from its 1000 samples: the shift in predictive mean in
      units of the pooled predictive sd; the ratio of 90 % interval widths; and the
      Wasserstein-1 distance between the two sample sets, also in units of the pooled sd.
  L5  from chap's evaluation files: the difference in aggregate CRPS, and per
      (location, split, horizon) row the difference in sample CRPS.

Draws no random numbers, so it takes no seed: every measure is computed from files.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

QUANTILES = (0.05, 0.25, 0.5, 0.75, 0.95)


# ---------------------------------------------------------------- run health
def health_label(crashed: bool, vb_aborted: float, nconfig: float, n_theta: float, mode_status: float) -> str:
    """One word for how a fit went. It describes; nothing is excluded on it (plan §4b,
    2026-10-17). 'crashed': no predictions. 'flagged': INLA logged a VB-correction abort,
    reported a non-zero mode status, or kept fewer than half of the CCD design's
    integration points (15 for 3 hyperparameters, 25 for 4). 'clean': none of these."""
    if crashed:
        return "crashed"
    expected = {3: 15, 4: 25}.get(int(n_theta), np.nan) if n_theta == n_theta else np.nan
    if (vb_aborted or 0) > 0 or (mode_status or 0) != 0 or (expected == expected and nconfig < expected / 2):
        return "flagged"
    return "clean"


# ---------------------------------------------------------------- L3
def read_posterior(run_dir: Path) -> pd.DataFrame:
    """All posterior summaries of a run as one table: group, name, mean, sd."""
    run_dir = Path(run_dir)
    parts = []
    hp = pd.read_csv(run_dir / "hyperpar.csv")
    parts.append(pd.DataFrame({"group": "hyperparameter", "name": hp["name"], "mean": hp["mean"], "sd": hp["sd"]}))
    fx = pd.read_csv(run_dir / "fixed.csv")
    parts.append(pd.DataFrame({"group": "fixed", "name": fx["name"], "mean": fx["mean"], "sd": fx["sd"]}))
    for f in sorted(run_dir.glob("random_*.csv")):
        term = f.stem[len("random_"):]
        rd = pd.read_csv(f)
        # a replicated term lists ID 1..n once per replicate, so the key is the position,
        # INLA's internal index (r - 1) * n + j (CH-22), with the ID kept for reading
        key = [f"{i + 1}:{v}" for i, v in enumerate(rd["ID"].astype(str))]
        parts.append(pd.DataFrame({"group": f"random:{term}", "name": key,
                                   "mean": rd["mean"], "sd": rd["sd"]}))
    return pd.concat(parts, ignore_index=True)


def compare_posterior(a: pd.DataFrame, b: pd.DataFrame) -> pd.DataFrame:
    """Per-quantity L3 measures; quantities present in only one run are kept with NaN."""
    m = a.merge(b, on=["group", "name"], how="outer", suffixes=("_a", "_b"))
    pooled = np.sqrt((m["sd_a"] ** 2 + m["sd_b"] ** 2) / 2)
    m["z_mean_shift"] = (m["mean_b"] - m["mean_a"]) / pooled
    m["sd_ratio"] = m["sd_b"] / m["sd_a"]
    return m


def summarise_posterior(m: pd.DataFrame) -> pd.DataFrame:
    """Per group: how many quantities, and the median and max |z| and sd-ratio range."""
    out = []
    for g, d in m.groupby("group", sort=False):
        z = d["z_mean_shift"].abs()
        out.append({"group": g, "n": len(d), "median_abs_z": z.median(), "max_abs_z": z.max(),
                    "sd_ratio_min": d["sd_ratio"].min(), "sd_ratio_median": d["sd_ratio"].median(),
                    "sd_ratio_max": d["sd_ratio"].max()})
    return pd.DataFrame(out)


# ---------------------------------------------------------------- L4
def read_samples(run_dir: Path) -> pd.DataFrame:
    p = Path(run_dir) / "predictions.csv.gz"
    return pd.read_csv(p).set_index(["time_period", "location"])


def compare_predictive(a: pd.DataFrame, b: pd.DataFrame) -> pd.DataFrame:
    """Per predicted row L4 measures. Rows are matched on (time_period, location)."""
    keys = a.index.intersection(b.index)
    A = np.sort(a.loc[keys].to_numpy(dtype=float), axis=1)
    B = np.sort(b.loc[keys].to_numpy(dtype=float), axis=1)
    if A.shape[1] != B.shape[1]:
        raise ValueError("sample counts differ")
    sd_a, sd_b = A.std(axis=1, ddof=1), B.std(axis=1, ddof=1)
    pooled = np.sqrt((sd_a ** 2 + sd_b ** 2) / 2)
    qa = np.quantile(A, QUANTILES, axis=1)
    qb = np.quantile(B, QUANTILES, axis=1)
    w1 = np.mean(np.abs(A - B), axis=1)  # equal sample counts: mean gap between order statistics
    with np.errstate(divide="ignore", invalid="ignore"):
        out = pd.DataFrame({
            "mean_a": A.mean(axis=1), "mean_b": B.mean(axis=1),
            "q50_a": qa[2], "q50_b": qb[2],
            "width90_a": qa[4] - qa[0], "width90_b": qb[4] - qb[0],
            "z_mean_shift": (B.mean(axis=1) - A.mean(axis=1)) / pooled,
            "width90_ratio": (qb[4] - qb[0]) / (qa[4] - qa[0]),
            "w1": w1, "w1_over_sd": w1 / pooled,
        }, index=keys)
    out["n_rows_only_a"] = len(a.index.difference(b.index))
    out["n_rows_only_b"] = len(b.index.difference(a.index))
    return out.reset_index()


def summarise_predictive(m: pd.DataFrame, future_periods: set | None = None) -> pd.DataFrame:
    """Median and 90th percentile of each L4 measure, for forecast rows and for historic
    rows with missing cases separately (chap scores only the forecast rows)."""
    groups = {"all": m}
    if future_periods is not None:
        fut = m["time_period"].isin(future_periods)
        groups = {"forecast_rows": m[fut], "historic_missing_rows": m[~fut]}
    out = []
    for g, d in groups.items():
        if len(d) == 0:
            continue
        row = {"rows": g, "n": len(d)}
        for col in ("z_mean_shift", "w1_over_sd"):
            v = d[col].abs()
            row[f"median_abs_{col}"] = v.median()
            row[f"p90_abs_{col}"] = v.quantile(0.9)
        r = d["width90_ratio"].replace([np.inf, -np.inf], np.nan)
        row["width90_ratio_median"] = r.median()
        row["width90_ratio_p10"] = r.quantile(0.1)
        row["width90_ratio_p90"] = r.quantile(0.9)
        out.append(row)
    return pd.DataFrame(out)


# ---------------------------------------------------------------- L5
def sample_crps(samples: np.ndarray, obs: np.ndarray) -> np.ndarray:
    """CRPS of an empirical forecast distribution, per row: E|X - y| - E|X - X'| / 2.

    Uses the sorted-sample identity E|X - X'| = 2 / n^2 * sum_i (2i - n - 1) x_(i).
    """
    x = np.sort(samples, axis=1)
    n = x.shape[1]
    term1 = np.mean(np.abs(x - obs[:, None]), axis=1)
    i = np.arange(1, n + 1)
    term2 = (2.0 / n ** 2) * np.sum((2 * i - n - 1) * x, axis=1)
    return term1 - term2 / 2


def compare_chap_rows(a: pd.DataFrame, b: pd.DataFrame) -> dict:
    """Paired per-row CRPS differences between two chap evaluations (rows keyed by
    location, time_period, horizon_distance; columns include 'crps')."""
    k = ["location", "time_period", "horizon_distance"]
    m = a[k + ["crps"]].merge(b[k + ["crps"]], on=k, suffixes=("_a", "_b"))
    d = m["crps_b"] - m["crps_a"]
    return {"n_rows": len(m), "mean_crps_a": m["crps_a"].mean(), "mean_crps_b": m["crps_b"].mean(),
            "mean_diff": d.mean(), "median_abs_diff": d.abs().median(), "p90_abs_diff": d.abs().quantile(0.9),
            "mean_abs_diff": d.abs().mean()}
