# Data
- data/raw/scorecards/*.json: the department's SRL scorecards (385 files). NEVER edit.
- data/processed/: matches.csv, deliveries.csv, checkpoints.csv built by `python src/build_dataset.py` (contract columns). SOURCE.txt marks it as real.
- data/external/b1_pred_over6.csv: B1's over-6 predictions, extracted from the PDF B1 supplied (769 rows; every interval is symmetric around its prediction, which is the validity check we used). Ask B1 for the original CSV.
- data/synthetic/: generator output used only for tests/fallback (`python src/make_synthetic.py`). Never report from it.

## How the scorecards map to the contract
| Source | Contract column |
|---|---|
| matchId | match_id (kept as the source number, same as B1's `match`; no prefix is invented) |
| innings[].teamName, order | team_a (batted first), team_b; batting_team/bowling_team |
| ballByBallSummaries tokens | deliveries: over (1-based), ball (delivery order incl. extras), runs_batter, runs_extras, wicket |
| wormAndManhattan cumulative fields | checkpoints: runs_so_far, wickets_down at the end of over_mark |
| innings[].runs | final_score |
| matchCommentary | winner, margin_runs, margin_wickets, toss_winner (initials matched to team names; empty if not matched) |
| timeStamp | date (YYYY-MM-DD; this is the scrape timestamp, not necessarily the playing date) |

## Token meanings (validated: per-over runs, per-over wickets, innings runs and extras all reconcile for every innings)
`4` bat runs, `w` wicket, `2w` wide (2 runs), `1l` leg bye, `1b` bye, `2n` no-ball (2 runs total = 1 extra + 1 off the bat).

## Empty by design (not in the source)
striker, non_striker, bowler, wicket_type, venue, position_in_series. series_id is empty for the 124 matches whose seriesName is "0".

## Excluded
71932768 (match status 509, unfinished) and 71932770 (one innings only).

## Known data traps
- Checkpoints exist only if the innings completed that over: 10 second innings have no over-15 checkpoint (chase finished earlier).
- Second-innings final_score is CENSORED: a chase stops when the target is passed, so it is not what the team would have scored.
- The scorecard timestamp is the scrape time, so date is unreliable for time-based splits.
