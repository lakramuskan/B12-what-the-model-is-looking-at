# B12 — What the Model Is Looking At

> **Track:** Sequence and Uncertainty  
> **Module:** B12 — What the Model Is Looking At  
> **Focus:** Explainable AI  
> **Team Size:** 4 Members

---

## 1. Overview

B12 — *What the Model Is Looking At* is an Explainable AI module for a
T20 cricket score prediction system.

A prediction such as **"Projected Score: 165"** tells us the result, but
not **why** the model produced that prediction.

The purpose of this module is to identify the factors that drive the
model's prediction and understand how their importance changes as the
innings progresses.

The module will therefore focus on making the prediction **interpretable,
understandable, and useful to another person** rather than treating the
model as a black box.

---

## 2. Problem Statement

Machine learning models can produce predictions without clearly
explaining the reasons behind them.

For cricket score prediction, it is important to answer questions such as:

- Which factors are influencing the predicted score?
- Which features are most important at different stages of the innings?
- Does feature importance change as more deliveries are played?
- Which combinations of features influence the prediction together?

B12 addresses these questions through explainable machine learning.

---

## 3. Objectives

The main objectives of this module are:

1. Identify the factors driving the score prediction.
2. Calculate feature importance using SHAP.
3. Analyse feature importance at different innings checkpoints.
4. Compare feature importance at overs **6, 10, 12 and 15**.
5. Identify at least one meaningful feature interaction.
6. Interpret the findings in cricket-related terms.
7. Produce a structured output that can be used by other modules.

The B12 roadmap specifically requires SHAP analysis at the four
checkpoints and comparison of how feature influence changes over the
innings. :contentReference[oaicite:1]{index=1}

---

## 4. Proposed Methodology

The planned workflow is:

```text
             Shared Cricket Dataset
                      │
                      ▼
               Data Preparation
                      │
                      ▼
             Checkpoint Models
             ┌────────┼────────┐
             ▼        ▼        ▼
           Over 6   Over 10  Over 12  Over 15
             │        │        │        │
             └────────┼────────┼────────┘
                      ▼
                 SHAP Analysis
                      │
                      ▼
             Feature Importance
                      │
                      ▼
          Checkpoint-wise Comparison
                      │
                      ▼
           Feature Interaction Analysis
                      │
                      ▼
            Cricket Interpretation
