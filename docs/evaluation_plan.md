# Evaluation Plan

# Baseline

A simple baseline will be established before judging the main model.

The baseline will provide a reference point for evaluating the performance of the prediction models used in the B12 Explainable AI module. The main model will only be considered useful if its performance and explanations can be meaningfully compared with this baseline.

The baseline results will be recorded in "experiments.csv" before the main experiments are conducted.

Evaluation

Results will not be reported from only one random run.

All experiments involving randomness will be repeated using at least 10 different random seeds. We will report the mean, standard deviation, best result, and worst result across the runs.

The evaluation will compare the baseline and the main model using the same data and evaluation procedure.

The data will be split at the match or series level rather than at the individual ball level, because deliveries from the same match are not independent.

Evaluation Metrics

For the prediction component, the following metrics will be considered:

- Mean Absolute Error (MAE)
- Root Mean Squared Error (RMSE)
- R² score

MAE measures the average absolute difference between the predicted and actual final score. RMSE gives greater weight to larger prediction errors, while R² measures how much variation in the target is explained by the model.

For the Explainable AI component, we will evaluate:

- Feature importance stability across different random seeds
- Feature importance at overs 6, 10, 12 and 15
- Changes in feature importance as the innings progresses
- Direction of feature contribution
- Stability and consistency of SHAP explanations
- Interpretability of the results in cricket terms

SHAP Explainability Methodology

SHAP (SHapley Additive exPlanations) will be used to explain the predictions of the checkpoint models.

SHAP assigns each input feature a contribution value for an individual prediction. A positive SHAP value indicates that the feature pushes the prediction towards a higher final score, while a negative SHAP value indicates that it pushes the prediction towards a lower final score.

For each checkpoint model, SHAP values will be calculated at:

- Over 6
- Over 10
- Over 12
- Over 15

Mean absolute SHAP values will be calculated for each feature to determine its overall importance.

The feature importance results will be stored in:

"results/feature_importance.csv"

with the following columns:

"over_mark, feature, importance, direction"

The results will then be compared across the four checkpoints to identify which features become more important, which become less important, and which remain relatively stable as the innings progresses.

SHAP Interaction Analysis

At least one meaningful feature interaction will be investigated.

An interaction occurs when the combined effect of two features on the prediction is different from considering their effects independently.

Potential interactions will be investigated between cricket-related variables such as current run rate, runs scored, wickets down, balls since boundary, and other features used by the model.

The strongest meaningful interaction will be selected and interpreted in cricket terms based on the actual SHAP interaction results.

No interaction will be claimed unless it is supported by the experimental results.

Robustness and Stability

The stability of the explanations will be checked across multiple random seeds.

We will examine whether the ranking of important features remains reasonably consistent across runs. Large changes in feature importance will be investigated rather than ignored.

We will also check whether the conclusions remain consistent across the four checkpoint overs.

Failure Analysis

The model and explanation method will be tested for possible failure cases, including:

- Large prediction errors
- Unstable SHAP explanations
- Unexpected changes in feature importance
- Missing or unusual input values
- Extreme match situations
- Features producing difficult-to-interpret explanations
- Cases where the model is confident but performs poorly

At least one representative failure case will be analysed in detail.

Comparison

Every major result will be reported with an appropriate comparison.

We will compare:

1. The main prediction model against the baseline.
2. Model performance across multiple random seeds.
3. Feature importance at overs 6, 10, 12 and 15.
4. SHAP explanations across different checkpoints.
5. Individual feature contributions and their interactions.

We will not report a performance number or feature-importance value without explaining what it is being compared against.

Reproducibility

All experiments will use a fixed default seed of 42 and will be repeated with additional seeds for robustness.

The exact Python environment, dependencies, input files, experiment configuration, and commands required to reproduce the results will be documented.

All final experimental results will be recorded in "experiments.csv".

The final evaluation should be reproducible by another team member using a fresh copy of the repository.

Expected Outcome

The evaluation will determine whether the prediction models provide stable and interpretable explanations and how the factors influencing the predicted final score change from over 6 to over 15.

The final analysis should answer the following question:

Which factors drive the prediction at different stages of a T20 innings, how do their contributions change over time, and how reliable are these explanations?
