<<<<<<< HEAD
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
=======
# Data Notes (owner: Pooja)
## matches.csv — one row per match
match_id, series_id, date, position_in_series, team_a, team_b, venue, toss_winner, winner, margin_runs, margin_wickets
## deliveries.csv — one row per ball
match_id, innings, over, ball, batting_team, bowling_team, striker, non_striker, bowler, runs_batter, runs_extras, wicket, wicket_type
## checkpoints.csv — one row per match/innings/over_mark
match_id, innings, over_mark, runs_so_far, wickets_down, current_run_rate, balls_since_boundary, final_score
## Rules
- Never rename columns; new columns at the end only
- Dates YYYY-MM-DD
- over_mark in 6, 10, 12, 15
- Missing = empty cell; zero means zero
- Keep ID prefixes (M0412, not 412)
>>>>>>> 2a81f3b (Add B12 project)
