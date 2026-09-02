# Data Notes


## Required Dataset


### matches.csv


One row per match.


Important columns:
- match_id
- series_id
- date
- team_a
- team_b
- venue
- toss_winner
- winner


### deliveries.csv


One row per ball.


Important columns:
- match_id
- innings
- over
- ball
- batting_team
- bowling_team
- striker
- bowler
- runs_batter
- runs_extras
- wicket


### checkpoints.csv


One row per match/innings/over checkpoint.


Important columns:
- match_id
- innings
- over_mark
- runs_so_far
- wickets_down
- current_run_rate
- balls_since_boundary
- final_score


## Important Rules


- Do not rename columns.
- Dates use YYYY-MM-DD.
- over_mark = 6, 10, 12, 15.
- Empty cell means missing.
- Zero means zero.
- IDs retain their prefixes.