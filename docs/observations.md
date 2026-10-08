# Things we did not expect (Week-2 requirement)
Computed by the pipeline from the REAL scorecards. Re-read each one yourselves and put it in your own words before submitting.
1. Not every innings reaches every checkpoint: innings missing a checkpoint, by over_mark: {6: 0, 10: 0, 12: 0, 15: 10}. The ones missing are chases that ended early, so later checkpoints over-represent innings that were still going.
2. The first innings averages 175 runs but the second 159, and the chasing side won 49% of matches. A chase stops when the target is passed, so second-innings final scores are censored, not what the team would have made.
3. The edge over the flat-run-rate baseline shrinks as the innings advances: baseline minus GBM RMSE is over 6: 13.6, over 10: 7.1, over 12: 5.6, over 15: 3.9 runs.
4. Last-two-over momentum features changed RMSE by at most 0.22 runs against the contract-only model, which is within the seed spread.
5. SHAP and permutation importance rank features differently (Spearman by over: 6: 0.95, 10: 0.74, 12: 0.93, 15: 0.90).
6. Data quirks: the source has no batter, bowler or venue identity, 124 matches have no series name, and the date field is the scrape time.
