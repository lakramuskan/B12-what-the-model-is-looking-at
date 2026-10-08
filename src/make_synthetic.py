"""Generate a SYNTHETIC stand-in for the faculty SRL files (contract-compliant columns).
Used only until the real starter files arrive in data/raw/. Do not report these results as real."""
import random
import sys
import numpy as np
import pandas as pd

SEED = 42
random.seed(SEED)
np.random.seed(SEED)

OVER_MARKS = [6, 10, 12, 15]
TEAMS = ["Falcons", "Rhinos", "Tigers", "Wolves", "Sharks", "Eagles"]


def simulate_innings(rng, strength):
    """Ball-by-ball innings. Scoring slows with wickets lost, accelerates in the last 5 overs."""
    rows, runs, wkts = [], 0, 0
    for over in range(20):
        for ball in range(1, 7):
            if wkts >= 10:
                return rows
            death = 1.5 if over >= 15 else 1.0
            wk_slow = 1.0 - 0.06 * wkts
            p = np.array([0.35, 0.30, 0.08, 0.01, 0.12 * death, 0.06 * death])
            p[:2] /= wk_slow ** 1.5
            p = p / p.sum()
            r = rng.choice([0, 1, 2, 3, 4, 6], p=p)
            r = int(round(r * strength))
            extra = int(rng.random() < 0.04)
            w = int(rng.random() < 0.045 * (1.4 if over >= 15 else 1.0))
            if w:
                wkts += 1
            runs += r + extra
            rows.append((over, ball, r, extra, w))
    return rows


def main(n_matches=800, out="data/synthetic"):
    rng = np.random.default_rng(SEED)
    matches, deliveries, checkpoints = [], [], []
    for i in range(1, n_matches + 1):
        mid = f"M{i:04d}"
        ta, tb = rng.choice(TEAMS, 2, replace=False)
        finals = []
        for inn in (1, 2):
            strength = rng.normal(1.0, 0.08)
            balls = simulate_innings(rng, strength)
            total = sum(b[2] + b[3] for b in balls)
            finals.append(total)
            bat, bowl = (ta, tb) if inn == 1 else (tb, ta)
            for (over, ball, r, ex, w) in balls:
                deliveries.append([mid, inn, over, ball, bat, bowl, "P01", "P02", "B01",
                                   r, ex, w, "bowled" if w else ""])
            for om in OVER_MARKS:
                sub = [b for b in balls if b[0] < om]
                if len(sub) < om * 6:  # innings already over -> no checkpoint
                    continue
                runs = sum(b[2] + b[3] for b in sub)
                wk = sum(b[4] for b in sub)
                since = 0
                for b in reversed(sub):
                    if b[2] >= 4:
                        break
                    since += 1
                checkpoints.append([mid, inn, om, runs, wk, round(runs / om, 2), since, total])
        winner = ta if finals[0] > finals[1] else tb
        matches.append([mid, f"S{(i - 1) // 10 + 1:03d}", f"2026-{1 + (i % 12):02d}-{1 + (i % 28):02d}",
                        (i - 1) % 10 + 1, ta, tb, f"Ground {i % 5 + 1}", ta, winner, "", ""])
    pd.DataFrame(matches, columns="match_id,series_id,date,position_in_series,team_a,team_b,venue,toss_winner,winner,margin_runs,margin_wickets".split(",")).to_csv(f"{out}/matches.csv", index=False)
    pd.DataFrame(deliveries, columns="match_id,innings,over,ball,batting_team,bowling_team,striker,non_striker,bowler,runs_batter,runs_extras,wicket,wicket_type".split(",")).to_csv(f"{out}/deliveries.csv", index=False)
    pd.DataFrame(checkpoints, columns="match_id,innings,over_mark,runs_so_far,wickets_down,current_run_rate,balls_since_boundary,final_score".split(",")).to_csv(f"{out}/checkpoints.csv", index=False)
    print(f"wrote synthetic data for {n_matches} matches to {out}")


if __name__ == "__main__":
    main(out=sys.argv[1] if len(sys.argv) > 1 else "data/synthetic")
