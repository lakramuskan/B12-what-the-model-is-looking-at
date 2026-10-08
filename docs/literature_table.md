# Literature Table
Found via web search on 2026-10-06 and checked against the abstract/landing page of each source. Three-line summaries are written from those abstracts. **Each member should still open and skim the full paper before the viva** (the review earns marks only if you can defend it). Entries 1-2 are the standard SHAP references and are cited from general knowledge: confirm volume/page details on the publisher site.

| # | Source | What they did | Data | What we can borrow / how it differs from B12 |
|---|---|---|---|---|
| 1 | Lundberg & Lee, "A unified approach to interpreting model predictions," NeurIPS 2017 | Defines SHAP: additive feature attributions based on Shapley values | General (any model) | Our core method and definition of per-prediction attribution |
| 2 | Lundberg et al., "From local explanations to global understanding with explainable AI for trees," Nature Machine Intelligence, 2020 | Fast exact TreeSHAP, global summaries and pairwise interaction values for tree ensembles | Medical and benchmark data | TreeExplainer and SHAP interaction values (our interaction analysis) |
| 3 | Kumar, Venkatasubramanian, Scheidegger, Friedler, "Problems with Shapley-value-based explanations as feature importance measures," ICML 2020 | Shows mathematical and human-centred problems when Shapley values are read as feature importance | Theory plus examples | Why we cross-check with permutation importance and never call importance "cause" |
| 4 | "From SHAP Scores to Feature Importance Scores," arXiv:2405.11766 (2024) | Argues exact SHAP scores can mislead as relative importance, proposes a more general formalism | Theory | Supports our caveat that SHAP ranks of small features should not be over-read |
| 5 | Abeysuriya, Fernando, Navarathna, "Beyond the Run-rate: Forecasting Framework for First Innings Score in T20 Cricket," MERCon 2023 | Deep neural network predicting first-innings score every over from match state, batter and bowler features | 5 years of T20I, 14 teams, tested on 2022 T20 World Cup | A prediction target and per-over setup like ours, but no explanation of what drives it |
| 6 | Gilbert, "Modelling First Innings Totals in T20 Cricket: Applications in the IPL," MSc dissertation, Univ. of Cape Town, 2023 | Compared logistic regression, trees, bagging, forests, boosting, SVM, ANN, naive Bayes for how many runs are enough | IPL, features incl. players, venue, toss, teams | Model-family comparison; simple models can win, matches our baseline-first stance |
| 7 | Raj, Sudarsan, Srivatsan, Indumathy, "Cricket Score Prediction using Player-Specific Performance and Dynamic Metrics," ICISD 2025 | Player-vs-player probability model feeding a regression for innings score | IPL ball-by-ball | Source of player-level features that the SRL data could support later |
| 8 | Bhatnagar et al., "Analyzing key factors influencing IPL cricket scores using explainability and multimodal data," J. Quantitative Analysis in Sports, 2025 (doi 10.1515/jqas-2025-0006) | H2O AutoML model of low first-innings scores with XAI tools to quantify feature influence | IPL 2008-2024 plus pitch/weather data | Closest prior work (XAI on T20 score); differs: match-level static factors, not how influence changes over the innings |
| 9 | "Winner prediction in an ongoing one day international cricket match," Journal of Sports Analytics (doi 10.3233/JSA-220735) | In-play win classifier (best accuracy about 85%) with SHAP to interpret it | ODI matches | Evidence that domain features help and that SHAP is accepted for in-play cricket models |
| 10 | "CAMP: A Context-Aware Cricket Players Performance Metric," arXiv:2307.13700 | Context-aware player metric; SHAP used to rank which batter/bowler features matter | Cricket player data (ICC ratings) | Example of reporting mean absolute SHAP in cricket; venue-type context idea |
| 11 | Bajaj, "Prediction of Player Performance for IPL and analysing the attributes involved, using Explainable AI," MSc thesis, NCI Ireland, 2023 | Compared XGBoost, decision tree, SVR, random forest by RMSE, then SHAP | IPL player data | Same pipeline shape (RMSE comparison, then SHAP); gradient boosting performed best there |

## Gap B12 fills
Prior cricket XAI work explains static, match-level or player-level factors. We found none that tracks how feature influence changes across within-innings checkpoints (6/10/12/15) with seed-level stability reported. This is our claimed contribution; state it cautiously ("we did not find") because our search was limited.

## Backup datasets (to confirm access before using)
1. Cricsheet ball-by-ball data (T20I/IPL), free: https://cricsheet.org
2. IPL ball-by-ball datasets on Kaggle (check licence before use)
Neither has been downloaded or verified by us yet.
