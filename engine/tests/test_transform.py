import pandas as pd
import pytest

from conftest import BRAZIL, ITALY, make_pass
from pnsm.transform import eligible_passes, passes_table


def run(events, team_id=BRAZIL, periods=(1, 2)):
    return eligible_passes(passes_table(events), team_id, periods)


# --- passes_table: only flattening, no rules -------------------------------------------

def test_table_keeps_missing_values():
    table = passes_table([make_pass(recipient_id=None, location=None, outcome="Incomplete")])
    row = table.iloc[0]
    assert row.outcome == "Incomplete"
    assert pd.isna(row.x) and pd.isna(row.y)
    assert table.recipient_id.isna().all()


def test_table_ignores_other_event_types():
    shot = {"id": "s", "index": 1, "period": 1, "minute": 0, "second": 0,
            "type": {"id": 16, "name": "Shot"}, "team": {"id": BRAZIL, "name": "Brazil"}}
    assert passes_table([shot, make_pass()]).shape[0] == 1


# --- eligible_passes: CLAUDE.md section 5.1 ---------------------------------------------

def test_completed_pass_without_outcome_enters():
    result = run([make_pass()])
    assert len(result.passes) == 1
    assert result.attempted == 1


def test_explicit_outcome_is_incomplete():
    result = run([make_pass(outcome="Incomplete"), make_pass(outcome="Out")])
    assert len(result.passes) == 0
    assert result.incomplete == 2


def test_missing_recipient_is_excluded():
    result = run([make_pass(recipient_id=None)])
    assert len(result.passes) == 0
    assert result.no_recipient == 1


@pytest.mark.parametrize("location", [None, (-1.0, 40.0), (60.0, 80.5), (121.0, 10.0)])
def test_missing_or_invalid_location_is_excluded(location):
    result = run([make_pass(location=location)])
    assert len(result.passes) == 0
    assert result.no_location == 1


def test_pitch_edges_are_valid():
    result = run([make_pass(location=(0.0, 0.0)), make_pass(location=(120.0, 80.0))])
    assert len(result.passes) == 2


def test_extra_time_period_is_excluded_and_not_attempted():
    result = run([make_pass(period=1), make_pass(period=3), make_pass(period=5)])
    assert len(result.passes) == 1
    assert result.period == 2
    assert result.attempted == 1


def test_other_team_is_not_counted_as_excluded():
    result = run([make_pass(team_id=BRAZIL), make_pass(team_id=ITALY, outcome="Incomplete")])
    assert result.attempted == 1
    assert result.incomplete == 0
    assert set(result.passes.team_id) == {BRAZIL}


def test_each_pass_counts_under_first_reason_only():
    # incomplete AND without recipient AND without location: counts only as "incomplete"
    result = run([make_pass(outcome="Incomplete", recipient_id=None, location=None)])
    assert (result.incomplete, result.no_recipient, result.no_location) == (1, 0, 0)


def test_set_pieces_enter_when_completed():
    result = run([make_pass(pass_type="Throw-in"), make_pass(pass_type="Corner"), make_pass(pass_type="Free Kick")])
    assert len(result.passes) == 3


def test_counts_always_add_up():
    events = [
        make_pass(), make_pass(), make_pass(outcome="Incomplete"),
        make_pass(recipient_id=None), make_pass(location=None), make_pass(period=4),
    ]
    r = run(events)
    assert r.attempted - r.incomplete - r.no_recipient - r.no_location == len(r.passes) == 2


# --- regression with real data (CLAUDE.md section 8) -----------------------------------

@pytest.mark.regression
@pytest.mark.parametrize("team_id, attempted, completed", [(BRAZIL, 471, 400), (ITALY, 309, 243)])
def test_final_attempted_and_completed(final_events, team_id, attempted, completed):
    result = eligible_passes(passes_table(final_events), team_id)
    assert result.attempted == attempted
    assert len(result.passes) == completed
    assert (result.no_recipient, result.no_location, result.period) == (0, 0, 0)
