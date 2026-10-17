"""L1 and L2: the Python model frame and cross-basis against the R reference's.

For each development dataset x config variant, builds the frame with the package's data
layer from the harness's fit inputs and config, writes it, and compares it with the frame
the instrumented R reference wrote (replicate 1; L1-L2 are identical across replicates,
03_referenceHarness answer 1).

Usage: compare_frame.py <harness results dir> <harness configs dir> <package dir> <out dir>
"""

import gzip
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

harness, configs, package, out = (Path(a) for a in sys.argv[1:5])
sys.path.insert(0, str(package))
from ewars_python.frame import build_frame, parse_config  # noqa: E402

DATASETS = ["monthly_ewars", "weekly_nicaragua"]
VARIANTS = ["default", "nlags_3_6", "no_covariates", "region_seasonal"]
(out / "frames").mkdir(parents=True, exist_ok=True)
rows, cols_detail = [], []
for ds in DATASETS:
    for var in VARIANTS:
        cfg = parse_config(configs / f"{var}.yml")
        mf = build_frame(harness / "inputs" / ds / "historic.csv", harness / "inputs" / ds / "future.csv", cfg)
        py = mf.df
        with gzip.open(out / "frames" / f"frame_{ds}_{var}.csv.gz", "wt") as fh:
            py.to_csv(fh, index=False)
        rdir = harness / "fits" / ds / var / "rep1"
        r = pd.read_csv(rdir / "model_frame.csv.gz", keep_default_na=False, na_values=["NA"], float_precision="round_trip")
        same_cols = list(r.columns) == list(py.columns)
        worst_num, worst_basis, str_mismatch, na_mismatch = 0.0, 0.0, 0, 0
        for c in r.columns:
            if c not in py.columns:
                cols_detail.append((ds, var, c, "missing in Python", ""))
                continue
            rv, pv = r[c], py[c]
            na_diff = int((rv.isna() != pv.isna()).sum())
            na_mismatch += na_diff
            if pd.api.types.is_numeric_dtype(rv) or c in ("ID_year", "month", "week"):
                rn = pd.to_numeric(rv, errors="coerce").to_numpy(dtype=float)
                pn = pd.to_numeric(pv, errors="coerce").to_numpy(dtype=float)
                both = ~np.isnan(rn) & ~np.isnan(pn)
                d = float(np.max(np.abs(rn[both] - pn[both]))) if both.any() else 0.0
                if c.startswith("basis_"):
                    worst_basis = max(worst_basis, d)
                else:
                    worst_num = max(worst_num, d)
                cols_detail.append((ds, var, c, "max_abs_diff", repr(d)))
            else:
                n_bad = int((rv.astype(str) != pv.astype(str)).sum())
                str_mismatch += n_bad
                cols_detail.append((ds, var, c, "string_mismatches", str(n_bad)))
            if na_diff:
                cols_detail.append((ds, var, c, "na_pattern_mismatches", str(na_diff)))
        # cross-basis attributes (L2): knots, boundary knots, df, lag
        attr_diff = 0.0
        if mf.bases:
            rattrs = json.loads((rdir / "crossbasis.json").read_text())
            for b, ra in zip(mf.bases, rattrs):
                attr_diff = max(attr_diff,
                                float(np.max(np.abs(np.array(b.attrs["argvar"]["knots"]) - np.array(ra["argvar"]["knots"])))),
                                float(np.max(np.abs(np.array(b.attrs["range"]) - np.array(ra["range"])))))
                if list(b.attrs["df"]) != list(ra["df"]) or list(b.attrs["lag"]) != list(ra["lag"]):
                    attr_diff = float("inf")
        rows.append({"dataset": ds, "variant": var, "n_rows_r": len(r), "n_rows_py": len(py),
                     "same_columns_in_order": same_cols, "frame_max_abs_diff": worst_num,
                     "basis_max_abs_diff": worst_basis, "basis_attr_max_abs_diff": attr_diff,
                     "string_mismatches": str_mismatch, "na_pattern_mismatches": na_mismatch,
                     "n_predicted_rows_py": len(mf.pred_idx)})
pd.DataFrame(rows).to_csv(out / "l1_l2_comparison.tsv", sep="\t", index=False)
pd.DataFrame(cols_detail, columns=["dataset", "variant", "column", "measure", "value"]).to_csv(
    out / "l1_l2_columns.tsv", sep="\t", index=False)
print(pd.DataFrame(rows).to_string())
