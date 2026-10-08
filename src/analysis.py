"""Phase 3 analyses: failure cases (out-of-fold), robustness (less data, outliers), SHAP vs permutation check.
Usage: PYTHONPATH=src python src/analysis.py"""
import random
import numpy as np
import pandas as pd
import shap
from sklearn.inspection import permutation_importance
from sklearn.model_selection import GroupKFold, GroupShuffleSplit

from data_loader import load_checkpoints, for_over, FEATURE_SETS, OVER_MARKS
from model import make_model, baseline_predict
from evaluate import rmse, summarize

SEED = 42
random.seed(SEED)
np.random.seed(SEED)
FEATS = FEATURE_SETS["V2_decollinear_momentum"]


def failures(df):
    cases, buckets = [], []
    for om in OVER_MARKS:
        d, X, y, g = for_over(df, om, FEATS)
        oof = np.zeros(len(d)); top, topv = [None] * len(d), np.zeros(len(d))
        for tr, te in GroupKFold(n_splits=5).split(X, y, g):
            m = make_model(SEED).fit(X.iloc[tr], y.iloc[tr])
            oof[te] = m.predict(X.iloc[te])
            sv = shap.TreeExplainer(m).shap_values(X.iloc[te])
            k = np.abs(sv).argmax(axis=1)
            for r, i in enumerate(te):
                top[i], topv[i] = FEATS[k[r]], sv[r, k[r]]
        d = d.assign(predicted=oof, error=oof - y.values, top_feature=top, top_shap=topv)
        worst = d.reindex(d["error"].abs().sort_values(ascending=False).index).head(25)
        cases.append(worst.assign(over_mark=om)[["over_mark", "match_id", "innings", "wickets_down", "runs_so_far",
                                                 "final_score", "predicted", "error", "top_feature", "top_shap"]])
        d["wk_bucket"] = pd.cut(d["wickets_down"], [-1, 0, 1, 2, 3, 10], labels=["0", "1", "2", "3", "4+"])
        for b, s in d.groupby("wk_bucket", observed=True):
            buckets.append([om, str(b), len(s), round(s["error"].abs().mean(), 2), round(s["error"].mean(), 2)])
        # collapse check: model over-predicts when many wickets fall in the next overs (unseen future)
    pd.concat(cases).round(2).to_csv("results/failure_cases.csv", index=False)
    pd.DataFrame(buckets, columns=["over_mark", "wickets_down", "n", "mean_abs_error", "mean_signed_error"]).to_csv("results/error_by_wickets.csv", index=False)


def robustness(df, n_seeds=10):
    rows = []
    for om in OVER_MARKS:
        d, X, y, g = for_over(df, om, FEATS)
        for frac in (1.0, 0.5, 0.1):
            for corrupt in (False, True):
                r, rb, rank = [], [], []
                full_imp = None
                for s in range(n_seeds):
                    tr, te = next(GroupShuffleSplit(1, test_size=0.25, random_state=s).split(X, y, g))
                    rng = np.random.default_rng(s)
                    tr = rng.choice(tr, max(20, int(len(tr) * frac)), replace=False)
                    m = make_model(s).fit(X.iloc[tr], y.iloc[tr])
                    Xe = X.iloc[te].copy()
                    if corrupt:  # 3% wild outliers: runs_so_far x3 (e.g. a unit/entry error)
                        idx = rng.choice(len(Xe), max(1, int(.03 * len(Xe))), replace=False)
                        Xe.iloc[idx, Xe.columns.get_loc("runs_so_far")] *= 3
                    r.append(rmse(y.iloc[te], m.predict(Xe)))
                    rb.append(rmse(y.iloc[te], baseline_predict(Xe, om)))
                    imp = np.abs(shap.TreeExplainer(m).shap_values(X.iloc[te])).mean(axis=0)
                    rank.append(imp)
                rank = np.array(rank)
                rows.append([om, frac, "outliers_3pct" if corrupt else "clean", round(np.mean(r), 2), round(np.std(r, ddof=1), 2),
                             round(np.mean(rb), 2), FEATS[int(np.argmax(rank.mean(axis=0)))], round(float(rank.std(axis=0).mean()), 3)])
    pd.DataFrame(rows, columns=["over_mark", "train_fraction", "test_inputs", "gbm_rmse_mean", "gbm_rmse_std",
                                "baseline_rmse_mean", "top_feature", "importance_std_mean"]).to_csv("results/robustness.csv", index=False)


def shap_vs_permutation(df):
    rows = []
    for om in OVER_MARKS:
        d, X, y, g = for_over(df, om, FEATS)
        tr, te = next(GroupShuffleSplit(1, test_size=0.25, random_state=0).split(X, y, g))
        m = make_model(0).fit(X.iloc[tr], y.iloc[tr])
        shp = np.abs(shap.TreeExplainer(m).shap_values(X.iloc[te])).mean(axis=0)
        pi = permutation_importance(m, X.iloc[te], y.iloc[te], n_repeats=10, random_state=0,
                                    scoring="neg_root_mean_squared_error").importances_mean
        for i, f in enumerate(FEATS):
            rows.append([om, f, round(shp[i], 3), round(pi[i], 3)])
    pd.DataFrame(rows, columns=["over_mark", "feature", "shap_importance", "permutation_rmse_increase"]).to_csv("results/shap_vs_permutation.csv", index=False)


def by_innings(df, n_seeds=10):
    """Does the explanation differ between setting (innings 1) and chasing (innings 2)? Separate models, no 'innings' feature.
    Note: innings-2 final_score is censored by the chase ending when the target is passed."""
    feats = [f for f in FEATS if f != "innings"]
    rows = []
    for inn in (1, 2):
        for om in OVER_MARKS:
            d, X, y, g = for_over(df[df.innings == inn], om, feats)
            imps, r, rb = [], [], []
            for s in range(n_seeds):
                tr, te = next(GroupShuffleSplit(1, test_size=0.25, random_state=s).split(X, y, g))
                m = make_model(s).fit(X.iloc[tr], y.iloc[tr])
                r.append(rmse(y.iloc[te], m.predict(X.iloc[te]))); rb.append(rmse(y.iloc[te], baseline_predict(X.iloc[te], om)))
                imps.append(np.abs(shap.TreeExplainer(m).shap_values(X.iloc[te])).mean(axis=0))
            imps = np.array(imps)
            for i, f in enumerate(feats):
                rows.append([inn, om, f, round(imps[:, i].mean(), 4), round(imps[:, i].std(ddof=1), 4), round(np.mean(r), 2), round(np.std(r, ddof=1), 2), round(np.mean(rb), 2), len(d)])
    pd.DataFrame(rows, columns=["innings", "over_mark", "feature", "importance", "importance_std", "gbm_rmse_mean", "gbm_rmse_std", "baseline_rmse_mean", "n_rows"]).to_csv("results/feature_importance_by_innings.csv", index=False)


if __name__ == "__main__":
    df = load_checkpoints()
    by_innings(df); print("by-innings done")
    failures(df); print("failures done")
    shap_vs_permutation(df); print("permutation check done")
    robustness(df); print("robustness done")
