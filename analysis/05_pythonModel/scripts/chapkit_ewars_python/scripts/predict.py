"""Fit the EWARS model on historic + future rows and write 1000 predictive samples per row
with missing cases, as the R original's predict.R does.

Usage: python scripts/predict.py --historic historic.csv --future future.csv --output predictions.csv
Reads config.yml from the working directory (chapkit writes it there).
Set EWARS_SEED to fix the random seed; otherwise it is derived from the inputs (see
ewars_python/model.py), so the same inputs give the same samples.
"""

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from ewars_python.model import predict_chap  # noqa: E402

parser = argparse.ArgumentParser()
parser.add_argument("--historic", default="historic.csv")
parser.add_argument("--future", default="future.csv")
parser.add_argument("--output", default="predictions.csv")
parser.add_argument("--config", default="config.yml")
parser.add_argument("--diagnostics-dir", default=os.getenv("EWARS_DIAGNOSTICS_DIR"),
                    help="if given, also write the fit's summaries (INLA's file names) here")
args = parser.parse_args()

print("Running predictions...")
print(f"Historic: {args.historic}\nFuture: {args.future}\nOutput: {args.output}")
seed = int(os.environ["EWARS_SEED"]) if os.getenv("EWARS_SEED") else None
predict_chap(args.historic, args.future, args.output, args.config, seed=seed, diagnostics_dir=args.diagnostics_dir)
print(f"Predictions written to {args.output}")
