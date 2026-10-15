"""Build the harness's fit inputs: one historic/future pair per development dataset, in
the shape chap-core hands the R model (CH-06, CH-12).

Source: the six-column development inputs chap evaluated in batch 2
(../01_referenceThroughChap/results/run1/inputs/, JC-05). The split is the last backtest
window chap uses: the final 3 periods (= prediction_periods) of every location are the
future, everything before is the history. Unlike chap's backtest, the future carries the
*observed* covariates rather than climatology forecasts (JC-14): the harness compares R and
Python on identical inputs, and needs no weather model in between.

What chap does to the files before the model sees them, reproduced here:
  - a `parent` column, "-", before `location`;
  - weekly periods as ISO weeks `YYYY-Www` (the input carries `YYYY-MM-DD/YYYY-MM-DD`,
    Monday to Sunday; the ISO year and week of the Monday);
  - rows ordered by location, then period;
  - the future file without `disease_cases`.
For the weekly dataset the history is then checked, row for row and value for value,
against the historic.csv chap itself wrote into the R service's workspace for the same
window in batch 2 (../01_referenceThroughChap/results/run1/weekly_workspace/).

Usage: make_fit_inputs.py <inputs_dir> <weekly_workspace_historic> <n_future> <out_dir>
"""

import sys
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

inputs_dir, ws_hist, n_future, out_dir = Path(sys.argv[1]), Path(sys.argv[2]), int(sys.argv[3]), Path(sys.argv[4])
COLS = ["time_period", "rainfall", "mean_temperature", "disease_cases", "population", "parent", "location"]


def iso_week(period: str) -> str:
    y, w, _ = date.fromisoformat(period.split("/")[0]).isocalendar()
    return f"{y}-W{w:02d}"


for name in ["monthly_ewars", "weekly_nicaragua"]:
    raw = pd.read_csv(inputs_dir / f"{name}.csv", dtype=str, keep_default_na=False)
    df = raw.copy()
    if "/" in df["time_period"].iloc[0]:
        df["time_period"] = df["time_period"].map(iso_week)
    df["parent"] = "-"
    df = df[COLS]
    order = df["location"] + "\x00" + df["time_period"]
    df = df.iloc[np.argsort(order.to_numpy(), kind="stable")].reset_index(drop=True)
    periods = sorted(df["time_period"].unique())
    fut_periods = set(periods[-n_future:])
    is_fut = df["time_period"].isin(fut_periods)
    hist, fut = df[~is_fut], df[is_fut].drop(columns="disease_cases")
    d = out_dir / name
    d.mkdir(parents=True, exist_ok=True)
    hist.to_csv(d / "historic.csv", index=False)
    fut.to_csv(d / "future.csv", index=False)
    print(f"{name}: {len(hist)} historic rows, {len(fut)} future rows; "
          f"future periods {sorted(fut_periods)}; locations {df['location'].nunique()}")

    if name == "weekly_nicaragua":
        ws = pd.read_csv(ws_hist)
        mine = pd.read_csv(d / "historic.csv")
        assert list(ws.columns) == list(mine.columns), (list(ws.columns), list(mine.columns))
        assert len(ws) == len(mine), (len(ws), len(mine))
        for c in ["time_period", "parent", "location"]:
            assert (ws[c].astype(str) == mine[c].astype(str)).all(), c
        for c in ["rainfall", "mean_temperature", "disease_cases", "population"]:
            a, b = ws[c].to_numpy(float), mine[c].to_numpy(float)
            assert np.array_equal(np.isnan(a), np.isnan(b)) and np.array_equal(a[~np.isnan(a)], b[~np.isnan(b)]), c
        print(f"{name}: history identical to chap's workspace historic.csv ({len(ws)} rows, every column)")
