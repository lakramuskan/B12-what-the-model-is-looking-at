# Message to B1 and B2 teams (send from Muskan, Week 2)

Hi, we are B12 (What the model is looking at). We consume your outputs, so we want to agree columns before anyone builds more.

To B1 (Score at six):
1. Can you share pred_over6 as a CSV, not PDF? The PDF text merges some rows.
2. Your `match` column holds numbers like 71617682. The data contract says match_id keeps prefixes (M0412). Which ID is canonical, and how do we join to checkpoints.csv?
3. Can you share the fitted over-6 model file (pickle/joblib) and the exact feature list and order it was trained on? SHAP needs the model and the feature matrix, not only predictions.

To B2 (The information curve):
1. Can you share the four checkpoint models (overs 6, 10, 12, 15) as saved files, with feature lists?
2. Which library (sklearn, xgboost, lightgbm)? We use shap.TreeExplainer if tree-based.
3. How was the train/test split made (by match or series)? We want to explain on held-out rows only.

Until we hear back, we run our own gradient boosting on checkpoints.csv so we are not blocked.
