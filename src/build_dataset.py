"""Convert the department's raw scorecard JSON files (data/raw/scorecards/*.json) into the three contract files
matches.csv, deliveries.csv, checkpoints.csv in data/processed/. Never edits data/raw.
Usage: python src/build_dataset.py [--raw data/raw/scorecards] [--out data/processed]

Source facts (validated by this script on every run):
  ballByBallSummaries[over][firstInnings|secondInnings] = comma-separated delivery tokens
      '4'  runs off the bat | 'w' wicket | '2w' wide (2 runs) | '1l' leg bye | '1b' bye | '2n' no-ball (2 runs total)
  wormAndManhattan[over][innings] = 'runs_in_over,wickets_in_over,cumulative_runs,cumulative_wickets'
Assumptions (documented in data/README.md): no-ball = 1 extra + (n-1) off the bat; striker/bowler/venue are not in the
source so those columns are left empty; innings that ended before an over mark have no checkpoint at that mark."""
import argparse, datetime, glob, json, os, random, re
import numpy as np
import pandas as pd

SEED = 42
random.seed(SEED)
np.random.seed(SEED)
OVER_MARKS = [6, 10, 12, 15]


def parse_token(t):
    """-> (runs_batter, runs_extras, wicket, is_legal_ball, is_bat_boundary)"""
    if t == "w":
        return 0, 0, 1, 1, 0
    n = int(re.sub(r"\D", "", t) or 0)
    kind = t[-1] if not t[-1].isdigit() else ""
    if kind == "w":
        return 0, n, 0, 0, 0
    if kind in ("l", "b"):
        return 0, n, 0, 1, 0
    if kind == "n":
        return max(n - 1, 0), 1, 0, 0, int(n - 1 in (4, 6))
    return n, 0, 0, 1, int(n in (4, 6))


def initials(name):
    return "".join(w[0] for w in name.replace("-", " ").split() if w.lower() != "srl").upper()


def parse_result(comm, teams, runs):
    m = re.match(r"\s*(.*?)\s+(?:have|has)?\s*won by (\d+) (run|wicket)", comm)
    if m:
        w = next((t for t in teams if t.lower().startswith(m.group(1).strip().lower()[:12])), m.group(1).strip())
        return w, (int(m.group(2)) if m.group(3) == "run" else ""), (int(m.group(2)) if m.group(3) == "wicket" else "")
    if runs[0] != runs[1]:
        return (teams[0] if runs[0] > runs[1] else teams[1]), "", ""
    return "", "", ""


def main(raw, out):
    matches, deliveries, checkpoints, skipped = [], [], [], []
    series_ids = {}
    for f in sorted(glob.glob(os.path.join(raw, "*.json"))):
        s = json.load(open(f))["doc"][0]["data"]["score"]
        mid = str(s["matchId"])
        if len(s["innings"]) != 2 or s["matchStatus"] != 4:
            skipped.append((mid, f"status={s['matchStatus']} innings={len(s['innings'])}"))
            continue
        teams = [i["teamName"] for i in s["innings"]]
        runs = [i["runs"] for i in s["innings"]]
        winner, mr, mw = parse_result(s["matchCommentary"], teams, runs)
        tm = re.search(r"Toss:\s*([A-Za-z]+)", s["matchCommentary"])
        toss = next((t for t in teams if tm and initials(t) == tm.group(1).upper()), "")
        sn = s.get("seriesName", "0")
        sid = "" if sn in ("0", "", None) else series_ids.setdefault(sn, f"S{len(series_ids) + 1:03d}")
        ts = int(re.search(r"\d+", s["timeStamp"]).group()) / 1000
        date = datetime.datetime.fromtimestamp(ts, datetime.timezone.utc).strftime("%Y-%m-%d")
        matches.append([mid, sid, date, "", teams[0], teams[1], "", toss, winner, mr, mw])
        for k, key in enumerate(["firstInnings", "secondInnings"]):
            inn = k + 1
            bat, bowl = teams[k], teams[1 - k]
            tot_runs = tot_ext = 0
            over_state = {}
            for ob, ow in zip(s["ballByBallSummaries"], s["wormAndManhattan"]):
                toks = [t for t in ob[key].split(",") if t]
                if not toks:
                    continue
                ov = ob["overNumber"]
                legal = 0
                for b, t in enumerate(toks, 1):
                    rb, re_, w, lg, bd = parse_token(t)
                    deliveries.append([mid, inn, ov, b, bat, bowl, "", "", "", rb, re_, w, ""])
                    tot_runs += rb + re_; tot_ext += re_
                    legal += lg
                a = [int(x) for x in ow[key].split(",")]
                over_state[ov] = dict(legal=legal, cum_runs=a[2], cum_wk=a[3], toks=toks)
            I = s["innings"][k]
            es = I["extrasSummary"]
            assert tot_runs == I["runs"], (mid, inn, "runs", tot_runs, I["runs"])
            assert tot_ext == es["byes"] + es["legByes"] + es["wides"] + es["noBalls"] + es["penalties"], (mid, inn, "extras", tot_ext)
            for om in OVER_MARKS:
                if om not in over_state or over_state[om]["legal"] != 6:
                    continue  # innings ended before completing this over
                since, found = 0, False
                for ov in range(om, 0, -1):
                    for t in reversed(over_state[ov]["toks"]):
                        rb, re_, w, lg, bd = parse_token(t)
                        if bd:
                            found = True; break
                        since += lg
                    if found:
                        break
                st = over_state[om]
                checkpoints.append([mid, inn, om, st["cum_runs"], st["cum_wk"], round(st["cum_runs"] / om, 2), since, I["runs"]])
    os.makedirs(out, exist_ok=True)
    pd.DataFrame(matches, columns="match_id,series_id,date,position_in_series,team_a,team_b,venue,toss_winner,winner,margin_runs,margin_wickets".split(",")).to_csv(f"{out}/matches.csv", index=False)
    pd.DataFrame(deliveries, columns="match_id,innings,over,ball,batting_team,bowling_team,striker,non_striker,bowler,runs_batter,runs_extras,wicket,wicket_type".split(",")).to_csv(f"{out}/deliveries.csv", index=False)
    pd.DataFrame(checkpoints, columns="match_id,innings,over_mark,runs_so_far,wickets_down,current_run_rate,balls_since_boundary,final_score".split(",")).to_csv(f"{out}/checkpoints.csv", index=False)
    pd.DataFrame(series_ids.items(), columns=["series_name", "series_id"]).to_csv(f"{out}/series_lookup.csv", index=False)
    open(f"{out}/SOURCE.txt", "w").write("real_scorecards\n")
    print(f"matches {len(matches)}, deliveries {len(deliveries)}, checkpoints {len(checkpoints)}; skipped {skipped}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", default="data/raw/scorecards")
    ap.add_argument("--out", default="data/processed")
    a = ap.parse_args()
    main(a.raw, a.out)
