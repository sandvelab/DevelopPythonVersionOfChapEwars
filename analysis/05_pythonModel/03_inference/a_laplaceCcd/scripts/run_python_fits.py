"""The Python model (candidate a) on the R harness's fit inputs: every development dataset x
config variant, n seeded replicates each, writing per run the files the instrumented R
reference writes (fit_info.json, hyperpar.csv, fixed.csv, random_*.csv, configs.csv,
predictions.csv.gz). The fit is deterministic; the replicates differ only in the sampler's
seed, derived per component from the project seed (readme-at-start.md rule).

Usage: run_python_fits.py <harness results> <configs dir> <package dir> <out dir> <n_reps>
"""

import hashlib
import sys
import time
from pathlib import Path

import pandas as pd

harness, configs, package, out = (Path(a) for a in sys.argv[1:5])
n_reps = int(sys.argv[5])
sys.path.insert(0, str(package))
from ewars_python.model import PROJECT_SEED, predict_chap  # noqa: E402


def component_seed(component: str) -> int:
    d = hashlib.sha256(f"{PROJECT_SEED}/{component}".encode()).digest()
    return 1 + int.from_bytes(d[:4], "big") % (2 ** 31 - 2)


rows = []
for ds in ["monthly_ewars", "weekly_nicaragua"]:
    for var in ["default", "nlags_3_6", "no_covariates", "region_seasonal"]:
        for r in range(1, n_reps + 1):
            run = out / "fits" / ds / var / f"rep{r}"
            run.mkdir(parents=True, exist_ok=True)
            seed = component_seed(f"python-fit/{ds}/{var}/rep{r}")
            t0 = time.time()
            predict_chap(harness / "inputs" / ds / "historic.csv", harness / "inputs" / ds / "future.csv",
                         run / "predictions.csv", configs / f"{var}.yml", seed=seed, diagnostics_dir=run)
            (run / "predictions.csv").unlink()  # the same table is kept as predictions.csv.gz
            rows.append({"dataset": ds, "variant": var, "replicate": f"rep{r}", "seed": seed,
                         "seconds": round(time.time() - t0, 2)})
            print(rows[-1], flush=True)
pd.DataFrame(rows).to_csv(out / "python_fits_timings.tsv", sep="\t", index=False)
