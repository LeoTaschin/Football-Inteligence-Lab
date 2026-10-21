import json
from pathlib import Path

import pytest

from conftest import BRAZIL, FINAL
from pnsm import export, load, names, validate
from pnsm.config import CollectionConfig
from pnsm.labels import LabelTarget, place_labels
from pnsm.sequences import goal_sequences

CONFIG = Path(__file__).parents[1] / "config" / "wc1970_brazil.yaml"
FIXTURES = Path(__file__).parent / "fixtures"


# --- labels --------------------------------------------------------------------------

def test_isolated_node_label_goes_below():
    assert place_labels([LabelTarget("a", 60, 40, 10, "Pelé")]) == {"a": "below"}


def test_close_nodes_get_different_sides():
    sides = place_labels([LabelTarget("a", 60, 40, 15, "Mazzola"), LabelTarget("b", 60, 44, 10, "Boninsegna")])
    assert sides["a"] != "below" or sides["b"] != "below"


def test_label_stays_inside_pitch():
    # a node on the bottom touchline cannot put its label below
    assert place_labels([LabelTarget("a", 60, 79, 10, "Everaldo")])["a"] != "below"


# --- collection notes ----------------------------------------------------------------

def row(completed, opp_completed, xg, opp_xg, score=(1, 0), opponent="Itália", name="Italy"):
    return {"completed": completed, "opponentCompleted": opp_completed, "xg": xg, "opponentXg": opp_xg,
            "score": list(score), "opponent": opponent, "opponentName": name, "note": None}


def test_notes_follow_rules_and_one_per_match():
    rows = [row(400, 300, 2.0, 1.0), row(450, 440, 0.5, 1.5, opponent="Inglaterra", name="England"),
            row(410, 200, 1.0, 0.5, opponent="Peru", name="Peru")]
    export._add_notes(rows, "Brazil")
    assert rows[0]["note"] is None
    assert rows[1]["note"] == "Único jogo em que o Brasil criou menos xG que o adversário, e venceu."
    assert rows[2]["note"] == "Maior diferença de passes da campanha: 210 a mais que o Peru."


# --- validation ----------------------------------------------------------------------

def test_export_fails_when_edges_do_not_add_up():
    cfg = CollectionConfig.from_yaml(CONFIG)
    meta = load.find_match(FINAL, cfg.competition_id, cfg.season_id)
    data = export.build_match(meta, load.load_events(FINAL), load.load_lineups(FINAL), cfg)
    data["teams"][0]["edges"][0]["n"] += 1
    with pytest.raises(validate.ValidationError, match="soma das conexões"):
        validate.check_match(data, load.load_events(FINAL), cfg.periods)


# --- regression ----------------------------------------------------------------------

@pytest.fixture(scope="module")
def cfg():
    return CollectionConfig.from_yaml(CONFIG)


@pytest.fixture(scope="module")
def all_matches(cfg):
    ids = load.fetch_season(cfg.competition_id, cfg.season_id, team=cfg.team)
    return [export.build_match(load.find_match(i, cfg.competition_id, cfg.season_id), load.load_events(i),
                               load.load_lineups(i), cfg) for i in ids]


@pytest.mark.regression
def test_every_match_passes_validation(all_matches):
    assert len(all_matches) == 6
    for m in all_matches:
        assert all(m["validation"].values()), m["match"]["id"]


@pytest.mark.regression
def test_fourth_goal_of_final():
    events, lineups = load.load_events(FINAL), load.load_lineups(FINAL)
    players = names.players_from_lineup(next(t for t in lineups if t["team_id"] == BRAZIL))
    goal = goal_sequences(events, BRAZIL, lambda p: players[p].name, lambda p: players[p].num)[-1]
    assert (goal["minute"], goal["scorer"], goal["passes"], goal["players"]) == (86, "Carlos Alberto", 9, 8)
    assert goal["duration"] == pytest.approx(29.9, abs=0.1)
    assert goal["steps"][0]["text"] == "Tostão recupera a bola no próprio campo"
    assert "Clodoaldo dribla quatro vezes e conduz pela esquerda" in [s["text"] for s in goal["steps"]]
    assert goal["steps"][-1]["text"] == "Carlos Alberto finaliza: gol"


@pytest.mark.regression
def test_replay_starts_after_opponent_touch(all_matches):
    # final, 36': same possession id as Brazil's attack, but the replay starts at Boninsegna's recovery
    goal = next(g for g in all_matches[-1]["goals"] if g["minute"] == 36)
    assert goal["scorer"] == "Boninsegna"
    assert goal["duration"] < 10


@pytest.mark.regression
def test_campaign_matches_design(cfg, all_matches):
    design = json.loads((FIXTURES / "campaign_design.json").read_text(encoding="utf-8"))
    c = export.build_collection(cfg, all_matches)

    s = c["summary"]
    assert (s["wins"], s["played"], s["goalsFor"], s["goalsAgainst"]) == (6, 6, 19, 7)
    assert (s["completed"], s["attempted"], s["xgFor"], s["xgAgainst"]) == (2490, 2908, 14.75, 8.53)
    assert s["morePassesThanOpponent"] == 6

    for got, exp in zip(c["matches"], design["matches"]):
        assert got["opponent"] == exp["opponent"]
        assert (got["score"], got["completed"], got["opponentCompleted"]) == (exp["score"], exp["completed"], exp["opponentCompleted"])
        assert (got["xg"], got["opponentXg"]) == (exp["xg"], exp["opponentXg"])
        assert (sorted(got["topPair"]["names"]), got["topPair"]["n"]) == (exp["topPair"], exp["topPairN"])
        assert (len(got["mini"]["nodes"]), len(got["mini"]["edges"])) == (exp["miniNodes"], exp["miniEdges"])
        assert (got["note"] is not None) == exp["hasNote"]

    assert [[p["name"], p["n"]] for p in c["topPassers"]] == design["topPassers"]
    missed = {p["name"]: p["missed"] for p in c["topPassers"]}
    assert missed["Gérson"] == ["Inglaterra", "Romênia"] and missed["Carlos Alberto"] == []
    assert c["scale"] == {"maxPasses": 74, "maxPair": 44}
    assert (c["country"], c["season"]) == ("México", "1970")
    assert [[sorted(p["names"]), p["n"]] for p in c["topPairs"]] == design["topPairs"]


@pytest.mark.regression
def test_player_names_are_stable_across_matches(cfg):
    seen: dict[int, str] = {}
    for match_id in load.fetch_season(cfg.competition_id, cfg.season_id, team=cfg.team):
        for team in load.load_lineups(match_id):
            for pid, player in names.players_from_lineup(team).items():
                assert seen.setdefault(pid, player.name) == player.name, (pid, seen[pid], player.name)
