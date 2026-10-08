# Viva prep: each member is asked individually. Know YOUR code and the pipeline.
Everyone must be able to answer: What does B12 do and why does the unit need it? What is SHAP in one minute? Why is the split by match? What was the baseline and why? What did you find, with spread? Where does the explanation fail?

| Person | Owns | Must be able to explain line by line |
|---|---|---|
| Muskan | Repo, integration, make_report.py, INTEGRATION.md | The data contract, B1/B2 interface, how results/ regenerate, assumptions that could break |
| Pooja | Data: build_dataset.py, data_loader.py, features.py, notebook 01, data_notes.md | How the scorecard tokens (4, w, 2w, 1l, 2n) become runs/wickets, how checkpoints and balls_since_boundary are computed, why 2 matches are excluded, the chase-censoring trap |
| Kunal | Model + explanation: model.py, train.py (SHAP part), plots.py | TreeExplainer, mean abs SHAP, direction via correlation, interaction values, why current_run_rate was dropped |
| Samarth | Evaluation: evaluate.py, analysis.py, evaluation_plan.md, experiments.csv | Baseline, 10 seeds and group split, stability, permutation cross-check, failure analysis, robustness |

Hard questions to rehearse:
- "Your SHAP and permutation importances disagree at over 12. Which do you trust?" (Neither blindly: SHAP explains the model's output, permutation measures loss in accuracy; correlated features split credit.)
- "Does high SHAP importance mean the feature causes runs?" (No: it explains the model, not cricket.)
- "Why is innings a top feature?" (Second-innings final scores are censored by the target; the model uses innings as a proxy. See paper VI-H.)
- "Why did momentum features not help?" (Consistent with little short-term memory; B5 tests this; do not claim more.)
- "You beat B1 by 1.5 runs. Is that real?" (Paired bootstrap CI excludes 0 but we do not know B1's features or validation; our model uses momentum features and a different split.)
- "Why is over 6 error so much larger than over 15?" (More of the innings is unseen.)
