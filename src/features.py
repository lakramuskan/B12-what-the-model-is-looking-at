"""Derived momentum features from deliveries.csv (checkpoints.csv alone has only 4 numeric predictors).
ASSUMPTION to verify on real data: `over` may be 0- or 1-indexed; we detect it from the minimum value."""
import random
import numpy as np
import pandas as pd

SEED = 42
random.seed(SEED)
np.random.seed(SEED)

OVER_MARKS = [6, 10, 12, 15]
MOMENTUM = ["runs_last2", "wickets_last2", "boundaries_last2", "dot_pct_last2"]


def add_momentum(cp, dl, window=2):
    dl = dl.copy()
    dl["oi"] = dl["over"] - dl["over"].min()          # 0-based over index
    dl["runs"] = dl["runs_batter"].fillna(0) + dl["runs_extras"].fillna(0)
    dl["boundary"] = (dl["runs_batter"] >= 4).astype(int)
    dl["dot"] = ((dl["runs_batter"] == 0) & (dl["runs_extras"] == 0)).astype(int)
    dl["wk"] = dl["wicket"].fillna(0).astype(int)
    parts = []
    for om in OVER_MARKS:
        w = dl[(dl["oi"] >= om - window) & (dl["oi"] < om)]
        a = w.groupby(["match_id", "innings"]).agg(
            runs_last2=("runs", "sum"), wickets_last2=("wk", "sum"),
            boundaries_last2=("boundary", "sum"), dots=("dot", "sum"), balls=("dot", "size")).reset_index()
        a["dot_pct_last2"] = a["dots"] / a["balls"]
        a["over_mark"] = om
        parts.append(a.drop(columns=["dots", "balls"]))
    return cp.merge(pd.concat(parts), on=["match_id", "innings", "over_mark"], how="left")
