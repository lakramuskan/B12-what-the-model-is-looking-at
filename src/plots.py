import random
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import shap
from sklearn.model_selection import GroupShuffleSplit

from data_loader import load_checkpoints, for_over, FEATURE_SETS, OVER_MARKS
from model import make_model

SEED = 42
random.seed(SEED)
np.random.seed(SEED)
H = "V2_decollinear_momentum"
OUT = "results/plots/"
SYN = "SYNTHETIC DATA - not a finding"


def stamp(ax, synthetic):
    if synthetic:
        ax.text(0.5, 0.5, SYN, transform=ax.transAxes, ha="center", va="center", rotation=25, alpha=.12, fontsize=16)


def main():
    df = load_checkpoints()
    syn = not df.attrs.get("real", True)
    imp = pd.read_csv("results/feature_importance.csv")
    piv = imp.pivot(index="feature", columns="over_mark", values="importance")
    sd = imp.pivot(index="feature", columns="over_mark", values="importance_std")
    fig, ax = plt.subplots(figsize=(8, 4.5))
    for f in piv.index:
        ax.errorbar(piv.columns, piv.loc[f], yerr=sd.loc[f], marker="o", capsize=2, label=f)
    ax.set_xticks(OVER_MARKS); ax.set_xlabel("over checkpoint"); ax.set_ylabel("mean |SHAP| (runs), ±std over 10 seeds")
    ax.set_title("How feature importance changes through the innings"); ax.legend(fontsize=7, ncol=2); stamp(ax, syn)
    plt.tight_layout(); plt.savefig(OUT + "importance_by_over.png", dpi=150); plt.close()

    perf = pd.read_csv("results/model_performance.csv")
    fig, ax = plt.subplots(figsize=(7, 4))
    for (fs, m), d in perf.groupby(["feature_set", "method"]):
        if m == "baseline_flat_run_rate" and fs != H:
            continue
        lab = "baseline (flat run rate)" if m.startswith("baseline") else f"GBM {fs.split('_')[0]}"
        ax.errorbar(d["over_mark"], d["rmse_mean"], yerr=d["rmse_std"], marker="o", capsize=3, label=lab)
    ax.set_xticks(OVER_MARKS); ax.set_xlabel("over checkpoint"); ax.set_ylabel("RMSE (runs), mean ± std, 10 seeds"); ax.legend(); stamp(ax, syn)
    plt.tight_layout(); plt.savefig(OUT + "rmse_by_over.png", dpi=150); plt.close()

    it = pd.read_csv("results/feature_interactions.csv"); it = it[it.feature_set == H]
    feats = FEATURE_SETS[H]
    fig, axs = plt.subplots(1, 4, figsize=(18, 4.5))
    for ax, om in zip(axs, OVER_MARKS):
        M = np.zeros((len(feats), len(feats)))
        for _, r in it[it.over_mark == om].iterrows():
            i, j = feats.index(r.feature_a), feats.index(r.feature_b)
            M[i, j] = M[j, i] = r.interaction_strength
        ax.imshow(M, cmap="viridis"); ax.set_title(f"over {om}")
        ax.set_xticks(range(len(feats))); ax.set_xticklabels(feats, rotation=90, fontsize=7)
        ax.set_yticks(range(len(feats))); ax.set_yticklabels(feats if om == 6 else [], fontsize=7)
    plt.suptitle("Pairwise SHAP interaction strength" + (f" ({SYN})" if syn else "")); plt.tight_layout()
    plt.savefig(OUT + "interactions_heatmap.png", dpi=130); plt.close()

    eb = pd.read_csv("results/error_by_wickets.csv")
    fig, ax = plt.subplots(figsize=(7, 4))
    for om, d in eb.groupby("over_mark"):
        ax.plot(d["wickets_down"], d["mean_abs_error"], marker="o", label=f"over {om}")
    ax.set_xlabel("wickets down at checkpoint"); ax.set_ylabel("mean |error| (runs), out-of-fold"); ax.legend(); stamp(ax, syn)
    plt.tight_layout(); plt.savefig(OUT + "error_by_wickets.png", dpi=150); plt.close()

    for om in (6, 15):  # beeswarm + dependence for the top interaction pair
        d, X, y, g = for_over(df, om, feats)
        tr, te = next(GroupShuffleSplit(1, test_size=0.25, random_state=0).split(X, y, g))
        m = make_model(0).fit(X.iloc[tr], y.iloc[tr]); Xe = X.iloc[te]
        sv = shap.TreeExplainer(m).shap_values(Xe)
        shap.summary_plot(sv, Xe, show=False); plt.title(f"SHAP summary, over {om}" + (" [SYNTHETIC]" if syn else ""))
        plt.tight_layout(); plt.savefig(OUT + f"shap_summary_over{om}.png", dpi=130); plt.close()
        srt = it[(it.over_mark == om) & (it.feature_a != "innings") & (it.feature_b != "innings")].sort_values("interaction_strength", ascending=False)
        top = srt.iloc[0]   # strongest pair excluding 'innings' (a data-censoring proxy)
        shap.dependence_plot(top.feature_a, sv, Xe, interaction_index=top.feature_b, show=False)
        plt.title(f"over {om}: {top.feature_a} x {top.feature_b}"); plt.tight_layout()
        plt.savefig(OUT + f"dependence_over{om}.png", dpi=130); plt.close()
    print("plots saved")


if __name__ == "__main__":
    main()
