# Results
All files regenerate with `make all` (see root README). Built from the real SRL scorecards.

## feature_importance.csv (THE HANDOVER)
- over_mark: checkpoint over (6, 10, 12, 15)
- feature: model input name (columns of checkpoints.csv, or derived from deliveries.csv: runs_last2, wickets_last2, boundaries_last2, dot_pct_last2). `innings` is a feature and is largely a proxy for the second-innings censoring (chase stops at target); do not read it as a cricket factor
- importance: mean absolute SHAP value over held-out rows, averaged over 10 seeds; unit = runs of predicted final score
- direction: positive = higher feature value raises the predicted score; negative = lowers it; mixed = |correlation| < 0.05
- importance_std: standard deviation of importance across the 10 seeds (runs)

## Supporting files
- feature_importance_all_sets.csv: same columns plus feature_set (V1_contract, V2_decollinear_momentum)
- feature_interactions.csv: over_mark, feature_a, feature_b, interaction_strength (mean |SHAP interaction| x 2, runs; 3 seeds, 300-row subsample), feature_set
- model_performance.csv: RMSE (runs) mean/std/best/worst over 10 seeds, for the baseline and the GBM, n_rows, rows_dropped_missing
- shap_stability.csv: mean and min Spearman rank correlation of feature-importance ordering between seeds
- shap_vs_permutation.csv: SHAP importance next to permutation importance (cross-check)
- failure_cases.csv: 25 largest out-of-fold errors per checkpoint, error = predicted - actual (runs), with the top SHAP feature
- error_by_wickets.csv: mean absolute and signed error by wickets down
- robustness.csv: RMSE with 100/50/10% of training data, with and without 3% corrupted test inputs
- feature_importance_by_innings.csv: separate models for innings 1 and 2 (no innings feature): importance, RMSE, baseline RMSE, n_rows
- b1_comparison.csv: B1 vs our out-of-fold model vs flat baseline on the same over-6 rows; paired bootstrap 95% CI of the RMSE gap (identical in each row, it describes the B1-minus-ours comparison); B1 interval coverage and width
- plots/: figures used in paper/paper.md

## Regenerate
    pip install -r requirements.txt
    make all

## Assumptions that must hold
1. Checkpoints are at overs 6, 10, 12, 15 only, and exist only if the innings was still in progress.
2. Rows with a missing feature or target are dropped (counted in model_performance.csv).
3. `over` in deliveries.csv is 1-based as in the scorecards; momentum features detect the base from the minimum value.
4. Explanations describe OUR gradient boosting model, not B1/B2 models, until their model files are integrated.
5. Second-innings final_score is censored by the chase ending at the target.
6. Importance is on the scale of predicted final score in runs. Compare ranks and shares, not raw values, across different models.
