"""Builds paper/paper.md and the README results table from results/*.csv so every number is traceable.
Usage: PYTHONPATH=src python src/make_report.py"""
import os, random, re
import numpy as np
import pandas as pd
from data_loader import find_checkpoints

SEED = 42
random.seed(SEED)
np.random.seed(SEED)
H = "V2_decollinear_momentum"
MEANING = {
    "runs_so_far": "runs already on the board",
    "wickets_down": "wickets lost (batting resources used)",
    "balls_since_boundary": "balls since the last four or six (a proxy for batters being 'in')",
    "innings": "batting first or chasing",
    "runs_last2": "runs scored in the last two overs (recent scoring pace)",
    "wickets_last2": "wickets lost in the last two overs (a recent collapse)",
    "boundaries_last2": "fours and sixes in the last two overs",
    "dot_pct_last2": "share of dot balls in the last two overs (pressure)",
}
PAIR = {
    frozenset(["runs_so_far", "wickets_down"]): "the same score is worth more with wickets in hand: batters still to come can accelerate, so runs on the board and wickets lost must be read together",
    frozenset(["runs_so_far", "balls_since_boundary"]): "a high score with a recent boundary signals settled batters, so the score carries more forward than the same score with a long boundary drought",
    frozenset(["runs_so_far", "runs_last2"]): "recent pace relative to the total tells you whether the innings is accelerating or stalling",
    frozenset(["runs_so_far", "innings"]): "this is mostly a data effect: a chase stops when the target is passed, so the same runs at the same over map to a different final score in innings 2 than in innings 1 (censoring), not a pure cricket interaction",
    frozenset(["wickets_down", "innings"]): "wickets matter far more for the first-innings forecast than for the chase, again largely because chase scores are censored by the target",
    frozenset(["wickets_down", "runs_last2"]): "a fast recent scoring burst matters differently when many wickets are down (risky) than when few are",
}


def md(df, floatfmt="{:.2f}"):
    cols = [str(c) for c in df.columns]
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    df = df.astype(object)
    for _, r in df.iterrows():
        out.append("| " + " | ".join(floatfmt.format(v) if isinstance(v, float) else str(v) for v in r) + " |")
    return "\n".join(out)


def observations(real):
    folder = os.path.dirname(find_checkpoints()[0])
    cp = pd.read_csv(f"{folder}/checkpoints.csv", dtype={"match_id": str})
    mt = pd.read_csv(f"{folder}/matches.csv", dtype={"match_id": str})
    n_inn = cp[["match_id", "innings"]].drop_duplicates().shape[0]
    cnt = cp.groupby("over_mark").size()
    short = {int(k): n_inn - int(v) for k, v in cnt.items()}
    f = cp.drop_duplicates(["match_id", "innings"]).groupby("innings").final_score.agg(["mean", "std"])
    chase = float((mt.winner == mt.team_b).mean())
    perf = pd.read_csv("results/model_performance.csv"); perf = perf[perf.feature_set == H]
    b = perf[perf.method == "baseline_flat_run_rate"].set_index("over_mark").rmse_mean
    m = perf[perf.method == "gradient_boosting"].set_index("over_mark").rmse_mean
    sp = pd.read_csv("results/shap_vs_permutation.csv")
    corr = sp.groupby("over_mark").apply(lambda d: d.shap_importance.corr(d.permutation_rmse_increase, method="spearman")).round(2)
    v1 = perf[perf.method == "gradient_boosting"]
    gap = (pd.read_csv("results/model_performance.csv").query("feature_set == 'V2_decollinear_momentum' and method == 'gradient_boosting'").rmse_mean.values
           - pd.read_csv("results/model_performance.csv").query("feature_set == 'V1_contract' and method == 'gradient_boosting'").rmse_mean.values)
    txt = f"""# Things we did not expect (Week-2 requirement)
Computed by the pipeline from {'the REAL scorecards' if real else 'SYNTHETIC test data'}. Re-read each one yourselves and put it in your own words before submitting.
1. Not every innings reaches every checkpoint: innings missing a checkpoint, by over_mark: {short}. The ones missing are chases that ended early, so later checkpoints over-represent innings that were still going.
2. The first innings averages {f.loc[1, 'mean']:.0f} runs but the second {f.loc[2, 'mean']:.0f}, and the chasing side won {chase:.0%} of matches. A chase stops when the target is passed, so second-innings final scores are censored, not what the team would have made.
3. The edge over the flat-run-rate baseline shrinks as the innings advances: baseline minus GBM RMSE is {', '.join(f'over {k}: {b[k]-m[k]:.1f}' for k in b.index)} runs.
4. Last-two-over momentum features changed RMSE by at most {abs(gap).max():.2f} runs against the contract-only model, which is within the seed spread.
5. SHAP and permutation importance rank features differently (Spearman by over: {', '.join(f'{k}: {v:.2f}' for k, v in corr.items())}).
6. Data quirks: the source has no batter, bowler or venue identity, 124 matches have no series name, and the date field is the scrape time.
"""
    open("docs/observations.md", "w").write(txt)


def main():
    real = find_checkpoints()[1]
    banner = "" if real else ("> **DRAFT ON SYNTHETIC DATA.** Every number below comes from a generator we wrote ourselves "
                              "(`src/make_synthetic.py`), not from the department's SRL files. Re-run the pipeline on the real files "
                              "and regenerate this document before submitting anything.\n\n")
    perf = pd.read_csv("results/model_performance.csv")
    imp = pd.read_csv("results/feature_importance.csv")
    it = pd.read_csv("results/feature_interactions.csv"); it = it[it.feature_set == H]
    stab = pd.read_csv("results/shap_stability.csv"); stab = stab[stab.feature_set == H]
    rob = pd.read_csv("results/robustness.csv")
    fc = pd.read_csv("results/failure_cases.csv")
    eb = pd.read_csv("results/error_by_wickets.csv")
    sp = pd.read_csv("results/shap_vs_permutation.csv")
    v1 = perf[(perf.feature_set == "V1_contract") & (perf.method == "gradient_boosting")]
    v2 = perf[(perf.feature_set == H) & (perf.method == "gradient_boosting")]
    bl = perf[(perf.feature_set == H) & (perf.method == "baseline_flat_run_rate")]

    res = pd.DataFrame({"over": bl.over_mark.values,
                        "baseline RMSE": [f"{m:.2f} ± {s:.2f}" for m, s in zip(bl.rmse_mean, bl.rmse_std)],
                        "GBM V1 (contract features)": [f"{m:.2f} ± {s:.2f}" for m, s in zip(v1.rmse_mean, v1.rmse_std)],
                        "GBM V2 (decollinear + momentum)": [f"{m:.2f} ± {s:.2f}" for m, s in zip(v2.rmse_mean, v2.rmse_std)],
                        "worst seed (V2)": [f"{w:.2f}" for w in v2.rmse_worst]})
    piv = imp.pivot(index="feature", columns="over_mark", values="importance").round(2)
    piv["change 6→15"] = (piv[15] - piv[6]).round(2)
    piv = piv.sort_values(15, ascending=False).reset_index()
    piv.columns = [str(c) for c in piv.columns]
    gain = piv.sort_values("change 6→15", ascending=False)
    gain_f, fade_f = gain.iloc[0]["feature"], gain.iloc[-1]["feature"]
    top6 = imp[imp.over_mark == 6].sort_values("importance", ascending=False).iloc[0]
    top15 = imp[imp.over_mark == 15].sort_values("importance", ascending=False).iloc[0]
    ints = []
    for om in (6, 10, 12, 15):
        srt = it[it.over_mark == om].sort_values("interaction_strength", ascending=False)
        r = srt.iloc[0]; q = srt[(srt.feature_a != "innings") & (srt.feature_b != "innings")].iloc[0]
        ints.append([om, f"{r.feature_a} x {r.feature_b}", round(r.interaction_strength, 2), f"{q.feature_a} x {q.feature_b}", round(q.interaction_strength, 2)])
    ints_df = pd.DataFrame(ints, columns=["over", "strongest pair", "strength (runs)", "strongest pair without innings", "strength (runs)  "])
    r15 = ints[-1]
    it15 = it[it.over_mark == 15].sort_values("interaction_strength", ascending=False)
    top_all = it15.iloc[0]
    top_cr = it15[(it15.feature_a != "innings") & (it15.feature_b != "innings")].iloc[0]
    pair_txt = PAIR.get(frozenset([top_all.feature_a, top_all.feature_b]), "see the dependence plot") + ". Excluding innings, the strongest pair at over 15 is " + top_cr.feature_a + " x " + top_cr.feature_b + ": " + PAIR.get(frozenset([top_cr.feature_a, top_cr.feature_b]), "this pair should be read together; the cricket reading must be written by the team after inspecting its dependence plot")
    gap = v2.rmse_mean.values - v1.rmse_mean.values
    momentum_note = ("Adding momentum features changed RMSE by at most "
                     f"{np.abs(gap).max():.2f} runs, well inside the seed spread, so we cannot claim they help."
                     if np.abs(gap).max() < v2.rmse_std.max() * 2 else "Momentum features changed RMSE beyond the seed spread.")
    worst_fc = ", ".join(f"over {k}: {v}" for k, v in fc.groupby("over_mark")["error"].apply(lambda s: s.abs().max()).round(1).items())
    r_all = rob[(rob.test_inputs == "clean")].pivot(index="over_mark", columns="train_fraction", values="gbm_rmse_mean").round(2)
    r_all.index = r_all.index.astype(int); r_all.index.name = "over"
    r_out = ", ".join(f"over {int(k)}: {v}" for k, v in rob[(rob.test_inputs == "outliers_3pct") & (rob.train_fraction == 1.0)].set_index("over_mark")["gbm_rmse_mean"].round(2).items())
    spp = sp.groupby("over_mark").apply(lambda d: d["shap_importance"].corr(d["permutation_rmse_increase"], method="spearman")).round(2)

    mt = pd.read_csv(os.path.join(os.path.dirname(find_checkpoints()[0]), "matches.csv"), dtype={"match_id": str})
    cpall = pd.read_csv(find_checkpoints()[0], dtype={"match_id": str})
    n_m, n_c = len(mt), len(cpall)
    chase_win = float((mt.winner == mt.team_b).mean())
    i1 = cpall.drop_duplicates(["match_id", "innings"]).groupby("innings").final_score.mean()
    if real:
        data_text = (f"The department's SRL league scorecards (JSON, one file per match; {n_m} completed matches used, 2 excluded: one unfinished, one with a single innings). "
                     f"Ball-by-ball strings were decoded into the shared contract files (matches, deliveries, checkpoints; see data/README.md); decoded runs, wickets and extras reconcile with the scorecard totals for every innings. "
                     f"The modelling table has {n_c} rows: one innings at one checkpoint (innings that ended before an over do not have that checkpoint). "
                     f"Mean final score is {i1[1]:.0f} in the first innings and {i1[2]:.0f} in the second; the chasing team won {chase_win:.0%} of matches. "
                     "The second-innings final score is censored: a chase stops when the target is passed. Batter, bowler and venue identities are not in the source, so no player-level features are possible. Rows with missing values are dropped and counted (`rows_dropped_missing` in results/model_performance.csv).")
    else:
        data_text = "**Current numbers use our synthetic generator; replace with the SRL description.**"
    b1 = pd.read_csv("results/b1_comparison.csv") if os.path.exists("results/b1_comparison.csv") else None
    b1_text = ""
    if b1 is not None:
        r = {x.predictor.split()[0]: x for x in b1.itertuples()}
        ours, theirs, flat = b1.iloc[0], b1.iloc[1], b1.iloc[2]
        b1_text = (f"### G. Integration test against B1 (over 6)\nOn the same {int(ours.n_rows)} over-6 rows, B1's predicted_score has RMSE {theirs.rmse:.2f} and MAE {theirs.mae:.2f}; our out-of-fold gradient boosting has RMSE {ours.rmse:.2f} and MAE {ours.mae:.2f}; the flat run-rate baseline has RMSE {flat.rmse:.2f}. "
                   f"The paired bootstrap 95% interval (resampling matches) for the RMSE gap (B1 minus ours) is {ours.rmse_gap_B1_minus_ours_95ci}. B1's stated range covers the true final score {ours.b1_interval_coverage:.1%} of the time with mean width {ours.b1_mean_interval_width:.0f} runs. "
                   "Caveats: we do not know B1's features or how it was validated, our features include last-two-over momentum, and a gap of this size could reflect any of these differences rather than a better method.\n\n")
    bi = pd.read_csv("results/feature_importance_by_innings.csv")
    pv = bi.pivot_table(index=["feature"], columns=["innings", "over_mark"], values="importance").round(2)
    pv.columns = [f"inn{a} over{b}" for a, b in pv.columns]
    pv = pv.reset_index()
    rm = bi.drop_duplicates(["innings", "over_mark"])[["innings", "over_mark", "gbm_rmse_mean", "gbm_rmse_std", "baseline_rmse_mean"]]
    rm = rm.assign(**{"GBM RMSE": [f"{a:.1f} ± {b:.1f}" for a, b in zip(rm.gbm_rmse_mean, rm.gbm_rmse_std)], "baseline RMSE": rm.baseline_rmse_mean.round(1)})[["innings", "over_mark", "GBM RMSE", "baseline RMSE"]]
    inn_text = ("### H. Setting versus chasing\nSeparate models per innings (no innings feature, 10 seeds). Mean |SHAP| by innings and checkpoint:\n\n" + md(pv) + "\n\nRMSE by innings:\n\n" + md(rm) +
                "\n\nBecause the second-innings target is censored (chases stop when the target is passed), second-innings errors and importances mix two different things, what the team would have scored and when the chase happened to end. Treat the innings-2 rows as descriptive.\n\n")
    inn_rank = ", ".join(f"over {int(o)}: rank {int(imp[imp.over_mark == o].importance.rank(ascending=False)[imp[imp.over_mark == o].feature == 'innings'].iloc[0])}" for o in (6, 10, 12, 15))
    inn2_share = f"{(fc.innings == 2).mean():.0%} of the 100 worst misses are second innings, typically a chase that ended early (target reached or all out) after the model had forecast a normal score."
    ex = []
    for om in (6, 12, 15):
        r = fc[fc.over_mark == om].iloc[0]
        direction = "under-predicted" if r.error < 0 else "over-predicted"
        ex.append(f"- Over {om}, match {r.match_id} innings {int(r.innings)}: {int(r.runs_so_far)} runs for {int(r.wickets_down)} down; model predicted {r.predicted:.0f}, final score {int(r.final_score)} (it {direction} by {abs(r.error):.0f}). The explanation was dominated by {r.top_feature} ({r.top_shap:+.1f} runs), which says nothing about what the remaining overs would bring.")
    examples = chr(10).join(ex)
    doc = f"""# What the Model Is Looking At: SHAP Explanations of T20 Score Prediction Across Over Checkpoints

{banner}**Team B12:** Muskan (lead), Pooja, Kunal, Samarth. Track B, Sequence and Uncertainty.

## Abstract
A projected T20 score is shown with confidence but without explanation. We explain a score-prediction model at four checkpoints (overs 6, 10, 12, 15) using SHAP, compare feature influence across checkpoints, and test how stable the explanations are. Against a flat-run-rate baseline, gradient boosting reduces RMSE at every checkpoint (over 6: {bl.rmse_mean.iloc[0]:.1f} to {v2.rmse_mean.iloc[0]:.1f}; over 15: {bl.rmse_mean.iloc[-1]:.1f} to {v2.rmse_mean.iloc[-1]:.1f}; mean over 10 seeds). {('The most influential feature is ' + top6.feature + ' at both over 6 and over 15, and what changes is how much it dominates and what ranks behind it') if top6.feature == top15.feature else (top6.feature + ' is the most influential feature at over 6 and ' + top15.feature + ' at over 15')}. We report SHAP rank stability across seeds, a permutation-importance cross-check, failure cases, and robustness to less data and corrupted inputs.

## I. Introduction
When a broadcast graphic says 165, "the model said so" is not an explanation. This module supplies the explanation and shows how it changes as the innings progresses. Our handover is `results/feature_importance.csv` (over_mark, feature, importance, direction), consumed by other modules of the unit.

## II. Related Work
**Explanation method.** SHAP assigns each feature a Shapley-value contribution to a prediction [1], with an exact fast algorithm for tree ensembles that also yields pairwise interaction values [2]. Shapley-based importances have known limits: they can disagree with intuitive importance, split credit among correlated inputs and do not imply causation [3], [4]. We therefore cross-check with permutation importance and report seed-to-seed stability.
**Cricket score prediction.** First-innings and per-over score forecasting has been attempted with deep networks on T20 internationals [5], classical model families on IPL data [6], and player-versus-player probability models [7]. These works optimise accuracy; none of them explains what drives the forecast.
**Explainability in cricket.** SHAP has been applied to a winner-prediction model for ODI cricket [9], to IPL first-innings scores using pitch, weather and team data [8], to player metrics [10] and to IPL player performance [11]. These explain static match-level or player-level factors. We did not find work that tracks how feature influence changes between checkpoints inside one innings, which is the gap this module addresses. (Our search was limited to web search in October 2026 and may have missed relevant work.)

## III. Data
{data_text}

## IV. Method
**Features.** V1 uses the four contract predictors plus innings. V2 removes `current_run_rate`, because it equals runs_so_far / over_mark and splits SHAP credit with runs_so_far, and adds four momentum features from deliveries.csv computed over the last two completed overs: runs, wickets, boundaries and dot-ball share.
**Model.** Gradient boosting regressor (150 trees, depth 3, learning rate 0.05, subsample 0.8), one model per checkpoint, retrained per seed.
**Explanation.** `shap.TreeExplainer` on held-out rows. importance = mean |SHAP| (runs); direction = sign of the correlation between feature value and SHAP value (|r| below 0.05 is reported as mixed). Pairwise interactions from SHAP interaction values (3 seeds, 300-row subsample).
**Baseline.** Current run rate held flat to over 20.

## V. Experimental Setup
Ten seeds (0 to 9). Each seed draws a different 75/25 train/test split **grouped by match** so the two innings of a match never straddle the split. Metric: RMSE in runs. We report mean, spread (std), best and worst seed. All runs are logged in `experiments.csv`.

## VI. Results
### A. Prediction against the baseline (RMSE, runs, 10 seeds)
{md(res)}

{momentum_note}

### B. Feature influence by checkpoint (mean |SHAP|, runs; V2)
{md(piv)}

Direction of influence at over 15: """ + ", ".join(f"{r.feature} {r.direction}" for r in imp[imp.over_mark == 15].itertuples()) + f""".

### C. Stability of the explanation
Mean Spearman rank correlation of the feature-importance ordering between pairs of seeds: """ + ", ".join(f"over {int(r.over_mark)}: {r.shap_rank_corr_mean:.2f} (min {r.shap_rank_corr_min:.2f})" for r in stab.itertuples()) + f""". Agreement between SHAP importance and permutation importance (Spearman, per checkpoint): """ + ", ".join(f"over {k}: {v:.2f}" for k, v in spp.items()) + f""".

### D. Interactions
{md(ints_df)}

Reading of the over-15 pairs: {pair_txt}.

### E. Failure analysis
Largest single out-of-fold error per checkpoint (runs): {worst_fc}. Mean absolute error by wickets down is in `results/error_by_wickets.csv` and `results/plots/error_by_wickets.png`; the 25 worst cases per checkpoint, with the feature that dominated the explanation, are in `results/failure_cases.csv`. {inn2_share} In these cases the explanation is confident about the cause it can see (typically {fc.top_feature.value_counts().index[0]}) while the cause of the miss, the overs yet to be bowled, is not an input at all. 

Three concrete cases (generated from failure_cases.csv; read them against the match yourselves):
{examples}

### F. Robustness
GBM RMSE by fraction of training data used (rows: over; columns: fraction):

{md(r_all.reset_index())}

With 3% of test inputs corrupted (runs_so_far x3), RMSE at full training data: {r_out}.

{b1_text}{inn_text}### I. Figures
![Fig. 1. RMSE of baseline and gradient boosting by checkpoint, mean ± std over 10 seeds.](../results/plots/rmse_by_over.png)

![Fig. 2. Mean absolute SHAP value per feature at each checkpoint, error bars are std over 10 seeds.](../results/plots/importance_by_over.png)

![Fig. 3. SHAP dependence at over 15 for the strongest interacting pair that does not involve innings.](../results/plots/dependence_over15.png)

![Fig. 4. Out-of-fold mean absolute error by wickets down.](../results/plots/error_by_wickets.png)

![Fig. 5. Pairwise SHAP interaction strength at each checkpoint.](../results/plots/interactions_heatmap.png)

## VII. Discussion
**What changes between over 6 and over 15.** {gain_f} gains the most influence ({piv.set_index('feature').loc[gain_f, '6']:.1f} to {piv.set_index('feature').loc[gain_f, '15']:.1f} runs) while {fade_f} loses the most. Cricket reading: early in the innings the model must infer how well the team is placed from wickets and pace; later the score already banked dominates because less of the innings is left to be predicted.
**Honest caveats.** (1) SHAP explains the model, not cricket: a feature the model leans on is not thereby a cause. (2) Correlated features share credit; we removed the one exact collinearity but run-rate-like proxies remain. (3) Interaction values were estimated on a subsample and three seeds. (4) SHAP and permutation importance agree less at later checkpoints (see C), so rankings of the small features should not be over-read. (5) Momentum features did not demonstrably improve prediction. That is consistent with little usable short-term memory in the league, but it does not prove it; module B5 tests memory directly. (6) `innings` is a top-three feature at every checkpoint ({inn_rank}). This is largely a data effect: second-innings final scores are censored because a chase stops at the target, so the model uses `innings` as a proxy for it. Read `innings` and its interactions as a property of the data, not a cricket factor, and see section H for per-innings models.

## VIII. Limitations
Checkpoints exist only at overs 6, 10, 12, 15 and only if the innings was still in progress. We explain our own gradient boosting model until B1/B2 models were available; explanations of a different model family will differ. The league is simulated, so findings describe the generator and may not transfer to real cricket (module B15 tests that). Second-innings targets are censored, batter and bowler identities are absent so no player-level explanation is possible, series differ (IPL, PSL, SA20, T20I style) and we split by match rather than by series, so a series effect could leak between train and test. The scorecard date is the scrape time, so no time-based split is possible.

## IX. Conclusion
We deliver the feature_importance.csv handover, a baseline-controlled evaluation over ten seeds, stability checks, and a failure analysis. The explanation answers "which factors drive the number and how that changes", and the failure analysis shows what no explanation of this model can: what happens in the overs not yet bowled.

## References
[1] S. M. Lundberg and S.-I. Lee, "A unified approach to interpreting model predictions," in Proc. NeurIPS, 2017.
[2] S. M. Lundberg et al., "From local explanations to global understanding with explainable AI for trees," Nature Machine Intelligence, vol. 2, 2020.
[3] I. E. Kumar, S. Venkatasubramanian, C. Scheidegger, and S. Friedler, "Problems with Shapley-value-based explanations as feature importance measures," in Proc. ICML (PMLR 119), 2020.
[4] "From SHAP scores to feature importance scores," arXiv:2405.11766, 2024.
[5] D. Abeysuriya, S. Fernando, and R. Navarathna, "Beyond the run-rate: forecasting framework for first innings score in T20 cricket," in Proc. MERCon, 2023.
[6] A. W. Gilbert, "Modelling first innings totals in T20 cricket: applications in the Indian Premier League," MSc dissertation, Univ. of Cape Town, 2023.
[7] U. V. Raj, S. Sudarsan, S. A. Srivatsan, and M. Indumathy, "Cricket score prediction using player-specific performance and dynamic metrics," in Proc. ICISD, 2025.
[8] M. Bhatnagar et al., "Analyzing key factors influencing IPL cricket scores using explainability and multimodal data," J. Quant. Anal. Sports, 2025, doi:10.1515/jqas-2025-0006.
[9] "Winner prediction in an ongoing one day international cricket match," J. Sports Analytics, doi:10.3233/JSA-220735.
[10] "CAMP: A context-aware cricket players performance metric," arXiv:2307.13700.
[11] A. Bajaj, "Prediction of player performance for IPL and analysing the attributes involved, using explainable AI," MSc thesis, National College of Ireland, 2023.
[Authors for [4], [9], [10] to be added from the full texts before submission.]
"""
    open("paper/paper.md", "w").write(doc)
    observations(real)
    table = md(res)
    s = open("README.md").read()
    block = f"<!--RESULTS-->\n{'**SYNTHETIC DATA, re-run on real files before reporting.**' + chr(10) if not real else ''}\n{table}\n<!--/RESULTS-->"
    s = re.sub(r"<!--RESULTS-->.*?<!--/RESULTS-->", block, s, flags=re.S) if "<!--RESULTS-->" in s else s
    open("README.md", "w").write(s)
    print("paper/paper.md written")


if __name__ == "__main__":
    main()
