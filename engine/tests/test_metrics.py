import json
import math
from pathlib import Path

import pytest

from conftest import BRAZIL, FINAL, ITALY, make_pass
from pnsm import load, metrics, names, transform

DEFENSIVE = ("Pressure", "Ball Recovery", "Interception", "Duel", "Clearance", "Block")


def network(events, team_id=BRAZIL):
    return transform.eligible_passes(transform.passes_table(events), team_id).passes


# --- nodes ---------------------------------------------------------------------------

def test_node_position_is_median_of_passes_made():
    passes = network([
        make_pass(player_id=10, location=(10, 10)),
        make_pass(player_id=10, location=(20, 30)),
        make_pass(player_id=10, location=(90, 70)),  # one far pass does not drag the median
    ])
    node = metrics.network_nodes(passes).loc[10]
    assert (node.x, node.y, node.passes) == (20, 30, 3)
    assert node.position_from == "passes"


def test_received_counts_completed_passes_to_player():
    passes = network([make_pass(player_id=10, recipient_id=8), make_pass(player_id=10, recipient_id=8),
                      make_pass(player_id=8, recipient_id=10)])
    nodes = metrics.network_nodes(passes)
    assert (nodes.loc[8].received, nodes.loc[10].received) == (2, 1)


def test_player_who_only_received_has_a_node():
    passes = network([make_pass(player_id=10, recipient_id=99, end_location=(100, 20)),
                      make_pass(player_id=10, recipient_id=99, end_location=(110, 30))])
    node = metrics.network_nodes(passes).loc[99]
    assert (node.passes, node.received, node.x, node.y) == (0, 2, 105, 25)
    assert node.position_from == "received"


def test_every_edge_endpoint_has_a_node():
    passes = network([make_pass(player_id=1, recipient_id=2), make_pass(player_id=2, recipient_id=3)])
    nodes = metrics.network_nodes(passes)
    edges = metrics.directed_edges(passes)
    assert set(edges.from_id) | set(edges.to_id) <= set(nodes.index)


# --- edges and pairs -----------------------------------------------------------------

def test_both_directions_are_kept_and_summed_in_pair():
    events = [make_pass(player_id=1, recipient_id=2)] * 3 + [make_pass(player_id=2, recipient_id=1)] * 2
    edges = metrics.directed_edges(network(events))
    assert {(r.from_id, r.to_id): r.n for r in edges.itertuples()} == {(1, 2): 3, (2, 1): 2}

    pair = metrics.pair_totals(edges).iloc[0]
    assert (pair.first_id, pair.second_id, pair.forward, pair.backward, pair.n) == (1, 2, 3, 2, 5)


def test_pair_lists_first_who_passed_more():
    events = [make_pass(player_id=1, recipient_id=2)] + [make_pass(player_id=2, recipient_id=1)] * 4
    pair = metrics.pair_totals(metrics.directed_edges(network(events))).iloc[0]
    assert (pair.first_id, pair.forward, pair.backward) == (2, 4, 1)


def test_edge_sum_equals_completed_passes():
    events = [make_pass(player_id=p, recipient_id=r) for p, r in [(1, 2), (2, 3), (3, 1), (1, 2)]]
    passes = network(events)
    assert metrics.directed_edges(passes).n.sum() == len(passes) == metrics.network_nodes(passes).passes.sum()


# --- shots ---------------------------------------------------------------------------

def make_shot(xg, outcome="Saved", period=1, team_id=BRAZIL):
    shot = {"outcome": {"id": 1, "name": outcome}, "end_location": [120, 40, 1]}
    if xg is not None:
        shot["statsbomb_xg"] = xg
    return {"id": f"s{xg}{outcome}", "index": 1, "period": period, "minute": 1, "second": 0,
            "type": {"id": 16, "name": "Shot"}, "team": {"id": team_id, "name": "T"},
            "player": {"id": 9, "name": "P"}, "location": [100, 40], "shot": shot}


def test_missing_xg_is_never_zero():
    shots = transform.shots_table([make_shot(0.5, "Goal"), make_shot(None), make_shot(0.1)], BRAZIL)
    assert math.isnan(shots.xg.iloc[1])
    summary = metrics.shot_summary(shots)
    assert (summary.count, summary.goals, summary.with_xg) == (3, 1, 2)
    assert summary.xg == pytest.approx(0.6)
    assert summary.mean_xg == pytest.approx(0.3)  # 0.6 / 2, not 0.6 / 3


def test_shootout_shots_are_excluded():
    shots = transform.shots_table([make_shot(0.7, period=2), make_shot(0.78, "Goal", period=5)], BRAZIL)
    assert len(shots) == 1


def test_shot_results_group_statsbomb_outcomes():
    outcomes = ["Goal", "Saved", "Saved to Post", "Saved Off Target", "Post", "Blocked", "Off T", "Wayward", "Something New"]
    shots = metrics.shot_list(transform.shots_table([make_shot(0.1, o) for o in outcomes], BRAZIL))
    assert list(shots.result) == ["goal", "saved", "saved", "saved", "post", "blocked", "off", "off", "other"]
    assert list(shots.outcome) == outcomes  # the original name is kept


def test_set_piece_comes_from_shot_type():
    events = [make_shot(0.1), make_shot(0.2)]
    events[0]["shot"]["type"] = {"id": 87, "name": "Open Play"}
    events[1]["shot"]["type"] = {"id": 62, "name": "Free Kick"}
    shots = metrics.shot_list(transform.shots_table(events, BRAZIL))
    assert list(shots.set_piece) == [False, True]
    assert list(shots.shot_type_code) == ["openPlay", "freeKick"]


def test_shot_list_is_chronological_and_keeps_missing_xg():
    late, early = make_shot(0.3), make_shot(None)
    late["index"], early["index"] = 50, 10
    shots = metrics.shot_list(transform.shots_table([late, early], BRAZIL))
    assert list(shots["index"]) == [10, 50]
    assert math.isnan(shots.xg.iloc[0])


@pytest.mark.parametrize("result, end, expected", [
    ("goal", (120, 40, 0.5), {"kind": "goal", "height": 0.5}),
    ("saved", (118, 39, None), {"kind": "saved", "height": None}),
    ("post", (120, 44, 1), {"kind": "post"}),
    ("blocked", (106, 40, None), {"kind": "blocked", "blockedAfter": 5.5}),  # 6 yd after the shot at x = 100
    ("off", (120, 40, 7.1), {"kind": "over", "height": 6.5, "wideBy": None}),
    ("off", (120, 56.1, 4.4), {"kind": "overWide", "height": 4.0, "wideBy": 11.1}),
    ("off", (120, 33.3, 0.2), {"kind": "wide", "height": 0.2, "wideBy": 2.5}),
    ("off", (110.6, 45.6, None), {"kind": "short"}),  # wayward: never reached the goal line
    ("other", (120, 40, 1), {"kind": "other"}),
])
def test_shot_finish(result, end, expected):
    assert metrics.shot_finish(result, 100, 40, *end) == expected


# --- cuts (CLAUDE.md 5.9) -------------------------------------------------------------

def test_first_sub_cut_is_by_event_index():
    events = [make_pass(), make_pass(), make_pass()]
    sub = {"index": events[1]["index"] + 0.5, "type": {"name": "Substitution"}, "team": {"id": BRAZIL}}
    passes = transform.eligible_passes(transform.passes_table(events), BRAZIL).passes
    cuts = transform.network_cuts(passes, transform.first_substitution_index([*events, sub], BRAZIL))
    assert list(cuts["firstSub"]["index"]) == [events[0]["index"], events[1]["index"]]


def test_team_without_subs_keeps_everything():
    passes = transform.eligible_passes(transform.passes_table([make_pass(), make_pass()]), BRAZIL).passes
    assert transform.first_substitution_index([], BRAZIL) is None
    assert len(transform.network_cuts(passes, None)["firstSub"]) == 2


def test_open_play_drops_set_pieces_but_keeps_recoveries():
    events = [make_pass(pass_type=t) for t in ("Free Kick", "Throw-in", "Goal Kick", "Corner", "Kick Off", "Recovery", "Interception")]
    events.append(make_pass())  # no pass.type: open play
    passes = transform.eligible_passes(transform.passes_table(events), BRAZIL).passes
    cuts = transform.network_cuts(passes, None)
    assert list(cuts["openPlay"].pass_type.fillna("-")) == ["Recovery", "Interception", "-"]
    assert transform.removed_set_pieces(passes) == {"Corner": 1, "Free Kick": 1, "Throw-in": 1, "Goal Kick": 1, "Kick Off": 1}


def test_cut_highlights_find_shift_and_drop():
    # player 1: 6 passes at x=60 in full, 5 at x=40 in the cut; player 2 loses 3 of 4 passes
    full_events = [make_pass(player_id=1, recipient_id=2, location=(60, 40)) for _ in range(6)]
    full_events += [make_pass(player_id=2, recipient_id=1, location=(50, 40)) for _ in range(4)]
    cut_events = [make_pass(player_id=1, recipient_id=2, location=(40, 40)) for _ in range(5)]
    cut_events += [make_pass(player_id=2, recipient_id=1, location=(50, 40))]
    full, cut = (metrics.network_nodes(network(e)) for e in (full_events, cut_events))
    h = metrics.cut_highlights(full, cut)
    assert (h.shift_id, h.shift_m) == (1, 18.3)  # 20 yd
    assert (h.drop_id, h.drop_from, h.drop_to) == (2, 4, 1)


def test_identical_cut_has_no_highlights():
    nodes = metrics.network_nodes(network([make_pass(player_id=1, recipient_id=2) for _ in range(5)]))
    assert metrics.cut_highlights(nodes, nodes) == metrics.CutHighlights(None, None, None, None, None)


# --- substitutions -------------------------------------------------------------------

def test_substitute_with_few_passes_keeps_node():
    passes = network([make_pass(player_id=1, recipient_id=2)] * 10 + [make_pass(player_id=12, recipient_id=1)])
    assert metrics.network_nodes(passes).loc[12].passes == 1


# --- regression: final vs the design canvas ------------------------------------------

# the design rounds to 0.1 with float noise (45.85 -> 45.9 but 6.55 -> 6.5), so positions match within 0.05
NEAR = 0.051
DESIGN = json.loads((Path(__file__).parent / "fixtures" / "final_design.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def final():
    events = load.load_events(FINAL)
    lineups = {t["team_id"]: names.players_from_lineup(t) for t in load.load_lineups(FINAL)}
    return events, lineups


@pytest.mark.regression
@pytest.mark.parametrize("team_id", [BRAZIL, ITALY])
def test_final_network_matches_design(final, team_id):
    events, lineups = final
    players = lineups[team_id]
    passes = network(events, team_id)
    nodes = metrics.network_nodes(passes)
    expected = DESIGN["teams"][str(team_id)]

    by_name = {players[pid].name: (pid, r) for pid, r in nodes.iterrows()}
    assert set(by_name) == {n["name"] for n in expected["nodes"]}
    for n in expected["nodes"]:
        pid, r = by_name[n["name"]]
        assert (players[pid].num, r.passes, r.received) == (n["num"], n["passes"], n["received"]), n["name"]
        assert (r.x, r.y) == (pytest.approx(n["x"], abs=NEAR), pytest.approx(n["y"], abs=NEAR)), n["name"]

    got_edges = {(players[r.from_id].name, players[r.to_id].name): r.n for r in metrics.directed_edges(passes).itertuples()}
    assert got_edges == {(a, b): n for a, b, n in expected["edges"]}


@pytest.mark.regression
def test_final_top_pairs(final):
    events, lineups = final
    for team_id, expected in [(BRAZIL, ("Gérson", "Carlos Alberto", 26, 18, 44)), (ITALY, ("Mazzola", "Domenghini", 10, 6, 16))]:
        top = metrics.pair_totals(metrics.directed_edges(network(events, team_id))).iloc[0]
        players = lineups[team_id]
        assert (players[top.first_id].name, players[top.second_id].name, top.forward, top.backward, top.n) == expected


@pytest.mark.regression
def test_final_most_used_italian_direction(final):
    events, lineups = final
    top = metrics.directed_edges(network(events, ITALY)).iloc[0]
    assert (lineups[ITALY][top.from_id].name, lineups[ITALY][top.to_id].name, top.n) == ("Albertosi", "Cera", 12)


@pytest.mark.regression
def test_final_shots_and_substitutions(final):
    events, lineups = final
    brazil = metrics.shot_summary(transform.shots_table(events, BRAZIL))
    italy = metrics.shot_summary(transform.shots_table(events, ITALY))
    assert (brazil.count, brazil.goals, round(brazil.xg, 2), brazil.with_xg) == (27, 4, 2.77, 27)
    assert (italy.count, italy.goals, round(italy.xg, 2), italy.with_xg) == (26, 1, 1.64, 26)

    assert metrics.substitutions(events, BRAZIL) == []
    subs = [(s.minute, lineups[ITALY][s.out_id].name, lineups[ITALY][s.in_id].name) for s in metrics.substitutions(events, ITALY)]
    assert subs == [(74, "Bertini", "Juliano"), (83, "Boninsegna", "Rivera")]


@pytest.mark.regression
def test_final_defensive_positions_match_design(final):
    events, lineups = final
    players = lineups[BRAZIL]
    positions = metrics.defensive_positions(transform.defensive_actions_table(events, BRAZIL, DEFENSIVE))
    by_name = {players[pid].name: r for pid, r in positions.iterrows()}
    expected = DESIGN["teams"]["781"]["defensive"]
    assert set(by_name) == {d["name"] for d in expected}
    for d in expected:
        r = by_name[d["name"]]
        assert r.n == d["n"], d["name"]
        assert (r.x, r.y) == (pytest.approx(d["x"], abs=NEAR), pytest.approx(d["y"], abs=NEAR)), d["name"]
