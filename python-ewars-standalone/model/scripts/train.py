"""Training is a no-op for this model, as in the R original's train.R: all fitting happens
at prediction time, on the historic and future rows together. This validates the input and
writes a placeholder model file.

Usage: python scripts/train.py --data <data.csv>
"""

import argparse
import json

import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument("--data", default="data.csv")
args = parser.parse_args()

print(f"Reading training data from: {args.data}")
df = pd.read_csv(args.data)
print(f"Training data shape: {df.shape[0]} rows x {df.shape[1]} columns")
print(f"Columns: {', '.join(df.columns)}")
with open("model.json", "w") as fh:
    json.dump({"trained": True, "n_rows": int(df.shape[0])}, fh)
print("Model placeholder saved to model.json")
