"""Integration test against B1 (Score at six): same rows, same metric. Out-of-fold predictions from our over-6 model
(5-fold grouped by match) vs B1's predicted_score; plus B1's interval coverage. Usage: PYTHONPATH=src python src/compare_b1.py"""
import os, random
import numpy as np
import pandas as pd
from sklearn.model_selection import GroupKFold

from data_loader import load_checkpoints, for_over, FEATURE_SETS
from model import make_model, baseline_predict

SEED = 42
random.seed(SEED)
np.random.seed(SEED)
FEATS = FEATURE_SETS["V2_decollinear_momentum"]


def main(path="data/external/b1_pred_over6.csv"):
    if not os.path.exists(path):
        print("no B1 file, skipping"); return
    df = load_checkpoints()
    d, X, y, g = for_over(df, 6, FEATS)
    oof = np.zeros(len(d))
    for tr, te in GroupKFold(5).split(X, y, g):
        oof[te] = make_model(SEED).fit(X.iloc[tr], y.iloc[tr]).predict(X.iloc[te])
    d = d.assign(ours=oof, flat=baseline_predict(X, 6))
    b1 = pd.read_csv(path, dtype={"match": str})
    j = d.merge(b1, left_on=["match_id", "innings"], right_on=["match", "innings"])
    e = lambda p: (j[p] - j["final_score"]).values
    rows = []
    rng = np.random.default_rng(SEED)
    mids = j["match_id"].unique()
    for name, p in (("B12 gradient boosting (out-of-fold)", "ours"), ("B1 predicted_score", "predicted_score"), ("flat run-rate baseline", "flat")):
        rows.append([name, round(float(np.sqrt((e(p) ** 2).mean())), 2), round(float(np.abs(e(p)).mean()), 2)])
    # paired bootstrap over matches: RMSE(B1) - RMSE(ours)
    diffs = []
    for _ in range(1000):
        samp = rng.choice(mids, len(mids), replace=True)
        s = pd.concat([j[j.match_id == m] for m in samp])
        diffs.append(np.sqrt(((s.predicted_score - s.final_score) ** 2).mean()) - np.sqrt(((s.ours - s.final_score) ** 2).mean()))
    lo, hi = np.percentile(diffs, [2.5, 97.5])
    cover = float(((j.final_score >= j.low_estimate) & (j.final_score <= j.high_estimate)).mean())
    width = float((j.high_estimate - j.low_estimate).mean())
    out = pd.DataFrame(rows, columns=["predictor", "rmse", "mae"])
    out["n_rows"] = len(j)
    out["rmse_gap_B1_minus_ours_95ci"] = f"[{lo:.2f}, {hi:.2f}]"
    out["b1_interval_coverage"] = round(cover, 3)
    out["b1_mean_interval_width"] = round(width, 1)
    os.makedirs("results", exist_ok=True)
    out.to_csv("results/b1_comparison.csv", index=False)
    print(out.to_string(index=False))


if __name__ == "__main__":
    main()
