"""Run after the pipeline: PYTHONPATH=src pytest -q tests   (or: make test)"""
import os
import pandas as pd

OVERS = {6, 10, 12, 15}


def test_handover_contract():
    d = pd.read_csv("results/feature_importance.csv")
    assert list(d.columns[:4]) == ["over_mark", "feature", "importance", "direction"]   # required order, extras only at end
    assert set(d.over_mark) == OVERS
    assert set(d.direction) <= {"positive", "negative", "mixed"}
    assert d.importance.ge(0).all() and d.importance.notna().all()
    assert not d.duplicated(["over_mark", "feature"]).any()
    assert d.groupby("over_mark").feature.apply(frozenset).nunique() == 1
    assert "current_run_rate" not in set(d.feature)


def test_baseline_reported_next_to_model_with_spread():
    p = pd.read_csv("results/model_performance.csv")
    assert {"baseline_flat_run_rate", "gradient_boosting"} <= set(p.method)
    assert (p.rmse_std > 0).all()


def test_experiment_log_columns():
    e = pd.read_csv("experiments.csv")
    assert list(e.columns) == "run_id,date,who,what_changed,main_metric,value,seed,notes".split(",")
    assert len(e) >= 8


def test_data_contract_columns():
    need = {"matches": "match_id,series_id,date,position_in_series,team_a,team_b,venue,toss_winner,winner,margin_runs,margin_wickets",
            "deliveries": "match_id,innings,over,ball,batting_team,bowling_team,striker,non_striker,bowler,runs_batter,runs_extras,wicket,wicket_type",
            "checkpoints": "match_id,innings,over_mark,runs_so_far,wickets_down,current_run_rate,balls_since_boundary,final_score"}
    for k, cols in need.items():
        assert list(pd.read_csv(f"data/processed/{k}.csv", nrows=1).columns) == cols.split(",")


def test_checkpoints_reconcile_with_deliveries():
    """Cumulative runs at each checkpoint must equal the sum of delivery runs to that over; final_score the innings total."""
    dl = pd.read_csv("data/processed/deliveries.csv", dtype={"match_id": str})
    cp = pd.read_csv("data/processed/checkpoints.csv", dtype={"match_id": str})
    dl["runs"] = dl.runs_batter + dl.runs_extras
    tot = dl.groupby(["match_id", "innings"]).runs.sum().rename("tot")
    assert (cp.join(tot, on=["match_id", "innings"]).eval("tot == final_score")).all()
    for om in OVERS:
        cum = dl[dl.over <= om].groupby(["match_id", "innings"]).runs.sum().rename("cum")
        c = cp[cp.over_mark == om].join(cum, on=["match_id", "innings"])
        assert (c.cum == c.runs_so_far).all(), om
    assert cp.over_mark.isin(OVERS).all()
    assert (cp.current_run_rate - cp.runs_so_far / cp.over_mark).abs().max() < 0.006


def test_ids_keep_source_format():
    m = pd.read_csv("data/processed/matches.csv", dtype={"match_id": str})
    assert m.match_id.str.fullmatch(r"\d{8}").all() and not m.match_id.duplicated().any()


def test_b1_join_is_complete():
    if os.path.exists("data/external/b1_pred_over6.csv"):
        b1 = pd.read_csv("data/external/b1_pred_over6.csv", dtype={"match": str})
        cp = pd.read_csv("data/processed/checkpoints.csv", dtype={"match_id": str})
        c6 = cp[cp.over_mark == 6]
        j = c6.merge(b1, left_on=["match_id", "innings"], right_on=["match", "innings"])
        assert len(j) == len(c6)           # every over-6 row has a B1 prediction
        assert ((b1.low_estimate < b1.predicted_score) & (b1.predicted_score < b1.high_estimate)).all()
