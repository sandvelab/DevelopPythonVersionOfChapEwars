"""Describe the CSVs in a chapkit workspace: the data a model script was actually given.

For every CSV: its shape, columns, time_period range, and for each numeric column that
should hold whole numbers (month, week, ID_year, ...) the values that are not exactly
whole, printed at full precision. Writes to stdout; the caller redirects to a file.

Usage: inspect_workspace.py <workspace_dir>
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

INTEGER_LIKE = ("month", "week", "ID_year", "year", "ID_time_cyclic")


def main(root: Path) -> None:
    files = sorted(p for p in root.rglob("*") if p.is_file())
    print(f"workspace: {root.name}")
    print("files:")
    for p in files:
        print(f"  {p.relative_to(root)}  {p.stat().st_size} bytes")
    for p in files:
        if p.suffix != ".csv":
            continue
        df = pd.read_csv(p)
        print(f"\n== {p.relative_to(root)}: {df.shape[0]} rows x {df.shape[1]} columns")
        print("columns:", ", ".join(f"{c}:{df[c].dtype}" for c in df.columns))
        if "time_period" in df.columns:
            tp = df["time_period"].astype(str)
            print(f"time_period: {tp.min()} .. {tp.max()}, e.g. {tp.iloc[0]!r}")
        for col in INTEGER_LIKE:
            if col not in df.columns or not np.issubdtype(df[col].dtype, np.number):
                continue
            v = df[col].dropna().to_numpy(dtype=float)
            bad = np.unique(v[v != np.round(v)])
            print(f"{col}: {len(v)} values, distinct {len(np.unique(v))}, not whole: {len(bad)}")
            for x in bad[:20]:
                print(f"    {x!r}")


if __name__ == "__main__":
    main(Path(sys.argv[1]))
