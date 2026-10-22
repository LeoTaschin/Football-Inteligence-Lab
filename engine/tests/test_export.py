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
def test_final_shot_map_matches_design(all_matches):
    brazil, italy = all_matches[-1]["teams"]
    assert (brazil["shots"]["count"], len(brazil["shots"]["items"]), italy["shots"]["count"]) == (27, 27, 26)

    goals = {s["name"]: s["xg"] for s in brazil["shots"]["items"] if s["result"] == "goal"}
    assert goals == {"Pelé": 0.058, "Gérson": 0.069, "Jairzinho": 0.719, "Carlos Alberto": 0.028}

    every = brazil["shots"]["items"] + italy["shots"]["items"]
    best = max(every, key=lambda s: s["xg"])
    assert (best["name"], best["minute"], best["xg"], best["result"]) == ("Pelé", 46, 0.794, "off")
    assert min(s["x"] for s in every) >= 80  # half a pitch is enough to draw them
    assert all_matches[-1]["scale"]["shotsFromX"] == 60

    top = [brazil["shots"]["items"][i] for i in brazil["shots"]["top"]]
    assert [(s["name"], s["xg"]) for s in top] == [("Pelé", 0.794), ("Jairzinho", 0.719), ("Tostão", 0.198),
                                                   ("Rivellino", 0.172), ("Tostão", 0.09)]
    carlos = next(s for s in brazil["shots"]["items"] if s["name"] == "Carlos Alberto" and s["result"] == "goal")
    assert carlos["distance"] == 19.7  # (12.5, 17.5) yd from the goal centre = 21.5 yd


@pytest.mark.regression
def test_shot_map_reaches_back_for_long_shots(all_matches):
    semi = next(m for m in all_matches if m["match"]["id"] == 3888701)
    assert semi["scale"]["shotsFromX"] == 40  # Pelé shoots from x = 45.9


@pytest.mark.regression
def test_final_cuts_match_design(all_matches):
    brazil, italy = all_matches[-1]["teams"]
    name = lambda team, pid: next(n["name"] for n in team["nodes"] if n["playerId"] == pid)
    bc, ic = brazil["cuts"], italy["cuts"]

    assert [bc[k]["completed"] for k in ("firstSub", "openPlay", "firstSubOpen")] == [400, 357, 357]
    assert bc["firstSub"]["sameAsFull"] and bc["firstSub"]["cutAt"] is None
    assert bc["openPlay"]["removed"] == {"Corner": 2, "Free Kick": 14, "Throw-in": 13, "Goal Kick": 12, "Kick Off": 2}
    shift = bc["openPlay"]["highlights"]["shift"]
    assert name(brazil, shift["playerId"]) == "Rivellino" and shift["meters"] == pytest.approx(11, abs=0.5)

    assert [ic[k]["completed"] for k in ("firstSub", "openPlay", "firstSubOpen")] == [193, 189, 148]
    assert ic["firstSub"]["cutAt"]["minute"] == 74 and name(italy, ic["firstSub"]["cutAt"]["out"]) == "Bertini"
    assert {n["name"] for n in ic["firstSub"]["nodes"]}.isdisjoint({"Juliano", "Rivera"})
    assert ic["openPlay"]["removed"] == {"Corner": 4, "Free Kick": 14, "Throw-in": 14, "Goal Kick": 17, "Kick Off": 5}
    drop = ic["openPlay"]["highlights"]["drop"]
    assert (name(italy, drop["playerId"]), drop["from"], drop["to"]) == ("Albertosi", 32, 12)


@pytest.fixture(scope="module")
def player_pages(cfg, all_matches):
    from pnsm import players
    collection = export.build_collection(cfg, all_matches)
    order = {r["id"]: (r["order"], r["stage"]) for r in collection["matches"]}
    return players.build_players(all_matches, order, cfg.min_pair_passes)


@pytest.mark.regression
def test_carlos_alberto_page_matches_design(player_pages):
    p = player_pages["carlos-alberto"]
    s = p["summary"]
    assert (s["games"], s["passes"], s["received"], s["share"]) == (6, 367, 361, 14.7)
    assert (s["teamRank"], s["topPasserGames"], round(s["avgShift"])) == (1, 3, -26)
    assert (p["to"][0]["name"], p["to"][0]["n"]) == ("Jairzinho", 108)
    assert (p["from"][0]["name"], p["from"][0]["n"]) == ("Clodoaldo", 82)
    final = p["games"][-1]
    assert (final["opponent"], final["passes"], final["rank"], final["partner"]["name"], final["partner"]["n"]) == ("Itália", 62, 2, "Gérson", 44)


@pytest.mark.regression
def test_opponent_has_a_single_game_page(player_pages):
    p = player_pages["mazzola"]
    assert (p["team"], p["summary"]["games"], p["summary"]["passes"], p["summary"]["share"]) == ("Itália", 1, 38, 15.6)
    assert p["games"][0]["opponent"] == "Brasil" and p["games"][0]["score"] == [1, 4]


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


@pytest.mark.regression
def test_committed_site_data_is_fresh(cfg):
    assert export.stale_files(cfg) == []


@pytest.mark.regression
def test_stale_detection_ignores_generated_at(tmp_path, cfg):
    from dataclasses import replace

    out = replace(cfg, output_dir=tmp_path)
    export.export_collection(out)
    assert export.stale_files(out) == []
    index = tmp_path / "index.json"
    data = json.loads(index.read_text(encoding="utf-8"))
    data["generatedAt"] = "1970-06-21T00:00:00Z"
    index.write_text(json.dumps(data), encoding="utf-8")
    assert export.stale_files(out) == []
    data["source"] = "outra fonte"
    index.write_text(json.dumps(data), encoding="utf-8")
    assert export.stale_files(out) == ["index.json"]
