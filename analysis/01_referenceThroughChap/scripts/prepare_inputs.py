"""Reduce a development CSV to the columns chap-core delivers to a model (JC-05).

The EWARS data contract (README of the pinned chapkit_ewars_model) is six columns:
time_period, rainfall, mean_temperature, disease_cases, population, location. The
monthly example file also carries columns predict.R would otherwise derive itself
(Cases, E, month, ID_year, ...). chap-core treats those as covariates and, in a
backtest, forecasts them for the future window, so `month` reaches R as 10.00000000000001
and INLA rejects the cyclic RW1 (CH-07). Rows and values are kept exactly; only columns
are dropped, and the file's unnamed index column with them.

Usage: prepare_inputs.py <in_csv> <out_csv>
"""

import sys

import pandas as pd

CONTRACT = ["time_period", "rainfall", "mean_temperature", "disease_cases", "population", "location"]

src, dst = sys.argv[1], sys.argv[2]
raw = pd.read_csv(src, dtype=str, keep_default_na=False)  # strings: values copied byte for byte
missing = [c for c in CONTRACT if c not in raw.columns]
if missing:
    sys.exit(f"{src}: missing contract columns {missing}")
raw[CONTRACT].to_csv(dst, index=False)
dropped = [c for c in raw.columns if c not in CONTRACT]
print(f"{src} -> {dst}: {len(raw)} rows; dropped columns: {dropped}")
