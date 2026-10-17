"""The data layer: a line-by-line port of predict.R's frame construction and lib.R.

Every function names the R lines it ports (chapkit_ewars_model @ 964eea8b). The R code's
quirks are reproduced, not corrected (JC-11): the cyclic index is the raw week or month
(so ISO week 53 is its own node), the year shift comes from the last row with observed
cases in frame order, and rows with missing cases are all predicted.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd
import yaml
from dlnmpy import crossbasis, equalknots

DEFAULT_CONFIG = {
    "n_lags": [3],
    "precision": 0.01,
    "region_seasonal": False,
    "additional_continuous_covariates": [],
}


def parse_config(config_path) -> dict:
    """predict.R parse_config: the flat YAML chapkit writes; R's defaults when absent.

    As in R, a missing config file means no covariates, and a missing field takes the
    R default. n_lags is kept as a list (R treats a scalar and a length-1 vector alike).
    """
    try:
        with open(config_path) as fh:
            config = yaml.safe_load(fh) or {}
    except FileNotFoundError:
        config = {}
    out = dict(DEFAULT_CONFIG)
    for key in out:
        if config.get(key) is not None:
            out[key] = config[key]
    out["n_lags"] = [int(v) for v in np.atleast_1d(out["n_lags"])]
    out["precision"] = float(out["precision"])
    out["region_seasonal"] = bool(out["region_seasonal"])
    out["additional_continuous_covariates"] = list(out["additional_continuous_covariates"] or [])
    return out


def read_csv_like_r(path) -> pd.DataFrame:
    """read.csv: empty fields and 'NA' are missing; numeric columns become float."""
    return pd.read_csv(path, keep_default_na=False, na_values=["", "NA"], float_precision="round_trip")


def apply_adapters(df: pd.DataFrame) -> pd.DataFrame:
    """predict.R apply_adapters: copy chap's names to the internal ones, keeping both."""
    alias_map = {"disease_cases": "Cases", "population": "E", "location": "ID_spat", "year": "ID_year"}
    for src, dst in alias_map.items():
        if src in df.columns and dst not in df.columns:
            df[dst] = df[src]
    return df


def _last_observed(df: pd.DataFrame, col: str) -> int:
    """lib.R get_last_week / get_last_month: the value in the last row with cases."""
    return int(df.loc[df["Cases"].notna(), col].iloc[-1])


def offset_years_and_weeks(df: pd.DataFrame) -> pd.DataFrame:
    """lib.R get_week_diff and offset_years_and_weeks."""
    last_week = _last_observed(df, "week")
    week_diff = 26 - last_week if last_week <= 26 else 78 - last_week
    new_week = df["week"] + week_diff
    df["week"] = ((new_week - 1) % 52) + 1
    df["ID_year"] = np.where(new_week > 52, df["ID_year"] + 1, df["ID_year"])
    return df


def offset_years_and_months(df: pd.DataFrame) -> pd.DataFrame:
    """lib.R get_month_diff and offset_years_and_months."""
    last_month = _last_observed(df, "month")
    month_diff = 6 - last_month if last_month <= 6 else 18 - last_month
    new_month = df["month"] + month_diff
    df["month"] = ((new_month - 1) % 12) + 1
    df["ID_year"] = np.where(new_month > 12, df["ID_year"] + 1, df["ID_year"])
    return df


@dataclass
class Basis:
    """One covariate's cross-basis, with the attributes R stores on it."""

    covariate: str
    matrix: np.ndarray  # n x (vx * vl), NaN where the lag reaches before a location's start
    colnames: list[str]
    attrs: dict


def build_crossbasis(df: pd.DataFrame, covariate: str, nlag: int) -> Basis:
    """predict.R generate_lagged_model, one covariate: dlnm::crossbasis via dlnmpy.

    lag = c(1, nlag); argvar = ns with knots equalknots(x, 2); arglag = ns with
    df = min(nlag, round(nlag / 2) + 2); group = the location label.
    """
    x = df[covariate].to_numpy(dtype=float)
    lag_df = min(nlag, _r_round(nlag / 2) + 2)
    cb = crossbasis(
        x,
        lag=(1, nlag),
        argvar={"fun": "ns", "knots": equalknots(x, 2)},
        arglag={"fun": "ns", "df": lag_df},
        group=df["ID_spat"].to_numpy(),
    )
    name = f"basis_{covariate}"
    return Basis(
        covariate=covariate,
        matrix=cb.matrix,
        colnames=[f"{name}.{c}" for c in cb.colnames],
        attrs={"df": list(cb.df), "range": list(cb.range), "lag": [int(v) for v in cb.lag],
               "argvar": cb.argvar, "arglag": cb.arglag, "group": cb.group},
    )


def _r_round(v: float) -> int:
    """R's round(): IEC 60559 round-half-to-even, which Python's round() also implements."""
    return int(round(v))


@dataclass
class ModelFrame:
    """Everything predict.R hands to inla(), plus what it needs to write the output."""

    df: pd.DataFrame  # the frame, columns as R's model data (basis columns included)
    fixed_names: list[str]  # "(Intercept)" then the basis columns, in formula order
    X: np.ndarray  # fixed-effects design, NaN basis values set to 0 (INLA's rule, CH-16)
    offset: np.ndarray  # log(E)
    y: np.ndarray  # Cases, NaN where predicted
    spat: np.ndarray  # ID_spat as 1-based integers
    year: np.ndarray  # ID_year, 1-based
    cyc: np.ndarray  # ID_time_cyclic
    cyc_values: np.ndarray  # sorted unique ID_time_cyclic (the RW1 nodes)
    region_seasonal: bool
    pred_idx: np.ndarray  # 0-based rows with missing cases
    bases: list[Basis] = field(default_factory=list)
    period: str = "month"


def build_frame(historic_fn, future_fn, config: dict) -> ModelFrame:
    """predict.R predict_chap, up to the inla() call."""
    historic = read_csv_like_r(historic_fn)
    future = read_csv_like_r(future_fn)
    if "disease_cases" not in future.columns:
        future["disease_cases"] = np.nan
    # rbind matches columns by name; the historic file's column order is kept
    df = pd.concat([historic, future[historic.columns]], ignore_index=True) if len(historic) else future.copy()

    df = apply_adapters(df)
    if "ID_year" not in df.columns:
        df["ID_year"] = df["time_period"].astype(str).str[:4].astype(int)
    if "week" not in df.columns and "month" not in df.columns:
        if "W" in str(df["time_period"].iloc[0]):
            df["week"] = df["time_period"].astype(str).str.replace(r".*W", "", regex=True).astype(int)
        else:
            df["month"] = df["time_period"].astype(str).str[5:7].astype(int)

    if "week" in df.columns:
        period = "week"
        df["ID_time_cyclic"] = df["week"]
        df = offset_years_and_weeks(df)
    else:
        period = "month"
        df["ID_time_cyclic"] = df["month"]
        df = offset_years_and_months(df)
    df["ID_time_cyclic2"] = df["ID_time_cyclic"]
    df["ID_year"] = df["ID_year"] - df["ID_year"].min() + 1

    covariates = config["additional_continuous_covariates"]
    nlag = config["n_lags"]
    if not (len(nlag) == 1 or len(nlag) == len(covariates)):
        raise ValueError("nlag must have length 1 or the same length as the number of covariates")
    if len(nlag) < len(covariates):
        nlag = nlag * len(covariates)
    bases = [build_crossbasis(df, cov, nlag[i]) for i, cov in enumerate(covariates)]
    for b in bases:
        df = pd.concat([df, pd.DataFrame(b.matrix, columns=b.colnames, index=df.index)], axis=1)

    # as.integer(as.factor(ID_spat)): levels in sorted order (JC-21 on the collation)
    levels = sorted(df["ID_spat"].astype(str).unique())
    df["ID_spat"] = df["ID_spat"].astype(str).map({lv: i + 1 for i, lv in enumerate(levels)}).astype(int)

    basis_cols = [c for b in bases for c in b.colnames]
    X = np.column_stack([np.ones(len(df))] + [np.nan_to_num(df[c].to_numpy(dtype=float), nan=0.0) for c in basis_cols])
    y = df["Cases"].to_numpy(dtype=float)
    cyc = df["ID_time_cyclic"].to_numpy(dtype=int)
    return ModelFrame(
        df=df,
        fixed_names=["(Intercept)"] + basis_cols,
        X=X,
        offset=np.log(df["E"].to_numpy(dtype=float)),
        y=y,
        spat=df["ID_spat"].to_numpy(dtype=int),
        year=df["ID_year"].to_numpy(dtype=int),
        cyc=cyc,
        cyc_values=np.unique(cyc),
        region_seasonal=config["region_seasonal"],
        pred_idx=np.flatnonzero(np.isnan(y)),
        bases=bases,
        period=period,
    )
