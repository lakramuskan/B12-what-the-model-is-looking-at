# B12 — Model and Explainability Plan

## 1. Objective

The objective of B12 is to explain which factors drive the score prediction and how their importance changes during the innings.

The module will focus on understanding the model's behaviour rather than reporting only the final predicted score.

## 2. Main Method

### SHAP — SHapley Additive exPlanations

SHAP will be used to estimate the contribution of each input feature to the model prediction.

SHAP values will help determine:

- Which features contribute most to the prediction.
- Whether a feature increases or decreases the predicted score.
- How feature influence changes at different stages of the innings.

## 3. Checkpoints

The analysis will be performed at four innings checkpoints:

- **Over 6**
- **Over 10**
- **Over 12**
- **Over 15**

The purpose is to compare how feature importance changes as the innings progresses.

## 4. Planned Analysis

The planned workflow is:

1. Load the appropriate checkpoint model.
2. Prepare the relevant input features.
3. Validate the feature data used by the model.
4. Calculate SHAP values.
5. Aggregate SHAP values to determine feature importance.
6. Determine the direction of each feature's influence.
7. Compare feature importance across overs 6, 10, 12 and 15.
8. Investigate meaningful feature interactions.
9. Identify changes in feature influence as the innings progresses.
10. Convert the findings into understandable cricket-related interpretations.

## 5. Feature Importance

Feature importance will be calculated using SHAP values.

A larger absolute SHAP contribution indicates a greater influence of a feature on the model's prediction for the analysed observations.

The analysis will consider:

- **Positive contribution:** pushes the prediction upward.
- **Negative contribution:** pushes the prediction downward.
- **Magnitude of contribution:** indicates the strength of the feature's influence.

## 6. Checkpoint Comparison

Feature importance will be compared across the four checkpoints to understand how the model's reasoning changes during the innings.

The analysis will examine:

- Which factors are important early in the innings.
- Which factors become more important in the middle overs.
- Whether important features change as the innings progresses.
- Which factors dominate near the end of the innings.

The comparison will focus on explaining these changes in cricket-related terms.

## 7. Feature Interaction Analysis

At least one meaningful interaction between features will be investigated.

The purpose is to determine whether the effect of one feature changes depending on the value of another feature.

The interaction will be interpreted in the context of cricket score prediction.

## 8. Final Output

The main output of the B12 module will be:

```text
results/feature_importance.csv
