import os
import random
import numpy as np
import pandas as pd
from features import add_momentum, MOMENTUM

SEED = 42
random.seed(SEED)
np.random.seed(SEED)

V1 = ["runs_so_far", "wickets_down", "current_run_rate", "balls_since_boundary", "innings"]
# V2 drops current_run_rate (= runs_so_far / over_mark, collinear) and adds momentum features
V2 = ["runs_so_far", "wickets_down", "balls_since_boundary", "innings"] + MOMENTUM
FEATURES = V1                      # kept for backward compatibility
FEATURE_SETS = {"V1_contract": V1, "V2_decollinear_momentum": V2}
TARGET = "final_score"
OVER_MARKS = [6, 10, 12, 15]


def find_checkpoints():
    """Return (path, is_real). Order: faculty CSVs in data/raw, then CSVs built from the real scorecards
    (python src/build_dataset.py), then the synthetic stand-in (tests only)."""
    if os.path.exists("data/raw/checkpoints.csv"):
        return "data/raw/checkpoints.csv", True
    if os.path.exists("data/processed/checkpoints.csv") and os.path.exists("data/processed/SOURCE.txt"):
        return "data/processed/checkpoints.csv", True
    if os.path.exists("data/synthetic/checkpoints.csv"):
        return "data/synthetic/checkpoints.csv", False
    raise FileNotFoundError("No data. Run: python src/build_dataset.py  (real scorecards in data/raw/scorecards)")


def load_checkpoints(path=None, with_momentum=True):
    real = True
    if path is None:
        path, real = find_checkpoints()
        if not real:
            print("WARNING: using SYNTHETIC data. Results are not valid for reporting.")
    df = pd.read_csv(path, dtype={"match_id": str})
    missing = set(V1 + [TARGET, "match_id", "over_mark"]) - set(df.columns)
    if missing:
        raise ValueError(f"checkpoints.csv missing columns: {sorted(missing)}")
    bad = set(df["over_mark"].unique()) - set(OVER_MARKS)
    if bad:
        raise ValueError(f"unexpected over_mark values: {sorted(bad)}")
    dpath = os.path.join(os.path.dirname(path), "deliveries.csv")
    if with_momentum and os.path.exists(dpath):
        dl = pd.read_csv(dpath, dtype={"match_id": str})
        df = add_momentum(df, dl)
    df.attrs["real"] = real
    return df


def for_over(df, over_mark, features):
    """Rows with any missing feature/target are dropped (missing = empty cell per contract); count is reported."""
    d = df[df["over_mark"] == over_mark].dropna(subset=features + [TARGET]).reset_index(drop=True)
    return d, d[features], d[TARGET], d["match_id"]
