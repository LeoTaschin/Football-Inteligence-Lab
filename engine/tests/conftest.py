import itertools

import pytest

from pnsm import load

BRAZIL = 781
ITALY = 914
FINAL = 3888702

_ids = itertools.count(1)


def make_pass(team_id=BRAZIL, player_id=10, recipient_id=8, period=1,
              location=(60.0, 40.0), end_location=(70.0, 30.0), outcome=None, pass_type=None):
    """Minimal StatsBomb Pass event. ``outcome=None`` means the key is absent (= completed)."""
    n = next(_ids)
    body = {"end_location": list(end_location)}
    if recipient_id is not None:
        body["recipient"] = {"id": recipient_id, "name": f"Player {recipient_id}"}
    if outcome is not None:
        body["outcome"] = {"id": 9, "name": outcome}
    if pass_type is not None:
        body["type"] = {"id": 61, "name": pass_type}
    event = {
        "id": f"ev-{n}", "index": n, "period": period, "minute": 10, "second": 0,
        "type": {"id": 30, "name": "Pass"}, "possession": 1,
        "team": {"id": team_id, "name": f"Team {team_id}"},
        "player": {"id": player_id, "name": f"Player {player_id}"},
        "pass": body,
    }
    if location is not None:
        event["location"] = list(location)
    return event


@pytest.fixture(scope="session")
def final_events():
    return load.load_events(FINAL)
