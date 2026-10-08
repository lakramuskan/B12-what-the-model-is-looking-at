import pandas as pd, json
H = "V2_decollinear_momentum"
p = pd.read_csv("results/model_performance.csv"); p = p[p.feature_set == H]
b = p[p.method == "baseline_flat_run_rate"]; m = p[p.method == "gradient_boosting"]
imp = pd.read_csv("results/feature_importance.csv")
piv = imp.pivot(index="feature", columns="over_mark", values="importance")
it = pd.read_csv("results/feature_interactions.csv"); it = it[(it.feature_set == H) & (it.over_mark == 15) & (it.feature_a != "innings") & (it.feature_b != "innings")]
top = it.sort_values("interaction_strength", ascending=False).iloc[0]
st = pd.read_csv("results/shap_stability.csv"); st = st[st.feature_set == H]
sp = pd.read_csv("results/shap_vs_permutation.csv")
corr = sp.groupby("over_mark").apply(lambda d: d.shap_importance.corr(d.permutation_rmse_increase, method="spearman")).round(2).tolist()
rob = pd.read_csv("results/robustness.csv")
clean = rob[rob.test_inputs == "clean"].pivot(index="over_mark", columns="train_fraction", values="gbm_rmse_mean")
out = rob[(rob.test_inputs == "outliers_3pct") & (rob.train_fraction == 1.0)].set_index("over_mark").gbm_rmse_mean
b1 = pd.read_csv("results/b1_comparison.csv")
fc = pd.read_csv("results/failure_cases.csv")
mt = pd.read_csv("data/processed/matches.csv")
d = dict(overs=[6, 10, 12, 15], base=b.rmse_mean.round(2).tolist(), basesd=b.rmse_std.round(2).tolist(), gbm=m.rmse_mean.round(2).tolist(), gbmsd=m.rmse_std.round(2).tolist(),
         imp={f: piv.loc[f].round(2).tolist() for f in piv.index}, stab=st.shap_rank_corr_mean.round(2).tolist(), perm=corr,
         pair=[top.feature_a, top.feature_b, float(round(top.interaction_strength, 2))],
         data_drop10=float(round(clean.loc[6, 0.1] - clean.loc[6, 1.0], 1)), out_lo=float(round((out - clean[1.0]).min(), 1)), out_hi=float(round((out - clean[1.0]).max(), 1)),
         b1=dict(ours=float(b1.rmse[0]), b1=float(b1.rmse[1]), flat=float(b1.rmse[2]), ci=b1.rmse_gap_B1_minus_ours_95ci[0], cover=float(b1.b1_interval_coverage[0])),
         inn2_share=float(round((fc.innings == 2).mean() * 100)), n_matches=int(len(mt)))
json.dump(d, open("slides/data.json", "w"), indent=1); print(d["b1"], d["inn2_share"])
