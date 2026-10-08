"""Main pipeline. For each feature set and checkpoint: baseline vs GBM over 10 seeds (split by match),
SHAP importance/direction/stability, SHAP interactions. Headline output = V2 feature set.
Usage: PYTHONPATH=src python src/train.py [--seeds 10] [--who NAME]"""
import argparse, csv, datetime, os, random
import numpy as np
import pandas as pd
import shap
from scipy.stats import spearmanr
from sklearn.model_selection import GroupShuffleSplit

from data_loader import load_checkpoints, for_over, FEATURE_SETS, OVER_MARKS
from model import make_model, baseline_predict
from evaluate import rmse, summarize, paired_gain

SEED = 42
random.seed(SEED)
np.random.seed(SEED)
HEADLINE = "V2_decollinear_momentum"


def next_run_id(path="experiments.csv"):
    if not os.path.exists(path):
        return 1
    with open(path) as f:
        return max(0, sum(1 for _ in f) - 1) + 1


def log(rows, path="experiments.csv"):
    new = not os.path.exists(path) or os.path.getsize(path) == 0
    with open(path, "a", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        if new:
            w.writerow("run_id,date,who,what_changed,main_metric,value,seed,notes".split(","))
        w.writerows(rows)


def run_set(df, name, feats, n_seeds, tag, who, rid, today):
    imp_rows, int_rows, perf_rows, stab_rows, log_rows = [], [], [], [], []
    for om in OVER_MARKS:
        d, X, y, g = for_over(df, om, feats)
        dropped = int((df["over_mark"] == om).sum() - len(d))
        base_r, model_r, imps, dirs = [], [], [], []
        inter = np.zeros((len(feats), len(feats)))
        for s in range(n_seeds):
            tr, te = next(GroupShuffleSplit(n_splits=1, test_size=0.25, random_state=s).split(X, y, g))
            m = make_model(s).fit(X.iloc[tr], y.iloc[tr])
            Xe = X.iloc[te]
            base_r.append(rmse(y.iloc[te], baseline_predict(Xe, om)))
            model_r.append(rmse(y.iloc[te], m.predict(Xe)))
            ex = shap.TreeExplainer(m)
            sv = ex.shap_values(Xe)
            imps.append(np.abs(sv).mean(axis=0))
            dirs.append([np.corrcoef(Xe[f], sv[:, i])[0, 1] if Xe[f].std() > 0 else 0.0 for i, f in enumerate(feats)])
            if s < 3:
                sub = Xe.sample(min(300, len(Xe)), random_state=s)
                inter += np.abs(ex.shap_interaction_values(sub)).mean(axis=0)
        imps, dirs = np.array(imps), np.array(dirs)
        for i, f in enumerate(feats):
            dr = np.nanmean(dirs[:, i])
            imp_rows.append([om, f, round(imps[:, i].mean(), 4), "positive" if dr > .05 else "negative" if dr < -.05 else "mixed",
                             round(imps[:, i].std(ddof=1), 4), name])
        inter /= 3
        for i in range(len(feats)):
            for j in range(i + 1, len(feats)):
                int_rows.append([om, feats[i], feats[j], round(2 * inter[i, j], 4), name])
        rhos = [spearmanr(imps[a], imps[b])[0] for a in range(n_seeds) for b in range(a + 1, n_seeds)]
        stab_rows.append([om, name, round(float(np.mean(rhos)), 3), round(float(np.min(rhos)), 3)])
        sb, sm = summarize(base_r), summarize(model_r)
        gain, gstd = paired_gain(base_r, model_r)
        perf_rows += [[om, name, "baseline_flat_run_rate", sb["mean"], sb["std"], sb["best"], sb["worst"], len(d), dropped],
                      [om, name, "gradient_boosting", sm["mean"], sm["std"], sm["best"], sm["worst"], len(d), dropped]]
        for label, st in ((f"baseline flat run rate{tag}", sb), (f"GBM {name}{tag}", sm)):
            log_rows.append([f"R{rid:03d}", today, who, f"{label} over {om}", "RMSE", round(st["mean"], 2), f"0-{n_seeds-1}",
                             f"std {st['std']:.2f}; best {st['best']:.2f}; worst {st['worst']:.2f}; split by match"])
            rid += 1
        print(f"[{name}] over {om}: baseline {sb['mean']:.2f}±{sb['std']:.2f} GBM {sm['mean']:.2f}±{sm['std']:.2f} "
              f"gain {gain:.2f}±{gstd:.2f}  SHAP rank stability rho={np.mean(rhos):.2f}")
    return imp_rows, int_rows, perf_rows, stab_rows, log_rows, rid


def main(n_seeds, who):
    df = load_checkpoints()
    real = df.attrs.get("real", True)
    tag = "" if real else " [SYNTHETIC]"
    today = datetime.date.today().isoformat()
    sets = {k: v for k, v in FEATURE_SETS.items() if all(f in df.columns for f in v)}
    if HEADLINE not in sets:
        print("WARNING: deliveries.csv not found, momentum features unavailable; falling back to V1")
    all_imp, all_int, all_perf, all_stab, all_log = [], [], [], [], []
    rid = next_run_id()
    for name, feats in sets.items():
        a, b, c, d_, e, rid = run_set(df, name, feats, n_seeds, tag, who, rid, today)
        all_imp += a; all_int += b; all_perf += c; all_stab += d_; all_log += e
    os.makedirs("results", exist_ok=True)
    imp = pd.DataFrame(all_imp, columns=["over_mark", "feature", "importance", "direction", "importance_std", "feature_set"])
    head = HEADLINE if HEADLINE in sets else list(sets)[0]
    imp[imp.feature_set == head].drop(columns="feature_set").to_csv("results/feature_importance.csv", index=False)
    imp.to_csv("results/feature_importance_all_sets.csv", index=False)
    pd.DataFrame(all_int, columns=["over_mark", "feature_a", "feature_b", "interaction_strength", "feature_set"]).to_csv("results/feature_interactions.csv", index=False)
    pd.DataFrame(all_perf, columns=["over_mark", "feature_set", "method", "rmse_mean", "rmse_std", "rmse_best", "rmse_worst", "n_rows", "rows_dropped_missing"]).to_csv("results/model_performance.csv", index=False)
    pd.DataFrame(all_stab, columns=["over_mark", "feature_set", "shap_rank_corr_mean", "shap_rank_corr_min"]).to_csv("results/shap_stability.csv", index=False)
    log(all_log)
    print("results written")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=10)
    ap.add_argument("--who", default="Muskan")
    a = ap.parse_args()
    main(a.seeds, a.who)
