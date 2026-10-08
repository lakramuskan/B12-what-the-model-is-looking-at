# Integration note — B12

## What I produce
results/feature_importance.csv — columns: over_mark, feature, importance (runs, mean |SHAP|), direction (positive/negative/mixed), importance_std (extra column at the end). Updated only when the pipeline is re-run (make all). Full column definitions: results/README.md.

## What I consume
- B1 (Score at six): pred_over6.csv — match, innings, predicted_score, low_estimate, high_estimate
- B2 (The information curve): the four checkpoint models (overs 6, 10, 12, 15) and information_curve.csv

## Assumptions that could break
1. Checkpoints are taken at overs 6, 10, 12 and 15 exactly. If that changes, our four-checkpoint comparison changes with it.
2. match_id is the source matchId (8-digit string, no prefix), identical to B1's `match` column.
3. SHAP needs fitted model objects plus the feature matrix, not only predictions. We currently explain our own gradient boosting model.
4. Second-innings final_score is censored by the chase target. Any module predicting final score (B1, B2, B4, B13) shares this issue.

## Tested against
- Real SRL scorecards (383 matches), decoded and reconciled to the scorecard totals (tests/test_pipeline.py).
- B1 over-6 predictions (data/external/b1_pred_over6.csv, extracted from B1's PDF): all 766 over-6 rows join on (match, innings). On those rows our out-of-fold model has RMSE 20.13, B1 21.59 (paired bootstrap 95% CI of the gap [0.92, 2.04]); B1's range covers the truth 90.7% of the time. See results/b1_comparison.csv.
- NOT yet run on B2's checkpoint models or information_curve.csv.

## Known incompatibilities
- B1 supplied a PDF, not a CSV. We parsed it (every interval symmetric around its prediction, 769 rows). B1 also predicted two matches we exclude (71932768 unfinished, 71932770 single innings).
- B1/B2 model files are not available, so importances describe our model and may differ from theirs.
- Our headline feature set drops current_run_rate (collinear with runs_so_far) and adds four last-two-over momentum features from deliveries.
