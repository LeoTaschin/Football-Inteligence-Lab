from pnsm.players import build_players, player_slugs


def team(team_id, name, nodes, edges, completed):
    return {"teamId": team_id, "name": name, "displayName": name, "article": "o", "colors": {},
            "passes": {"completed": completed}, "nodes": nodes, "edges": edges,
            "pairs": [{"a": e["from"], "b": e["to"], "forward": e["n"], "backward": 0, "n": e["n"]} for e in edges]}


def node(pid, name, passes, received=0):
    return {"playerId": pid, "name": name, "num": pid, "position": None, "ball": {"x": 60, "y": 40}, "def": None,
            "shift": None, "passes": passes, "received": received, "sub": None, "positionFrom": "passes"}


def match(mid, home_nodes, home_edges, completed):
    away = team(2, "B", [node(99, "Rival", 1)], [], 1)
    return {"match": {"id": mid, "score": [1, 0]}, "teams": [team(1, "A", home_nodes, home_edges, completed), away]}


def test_same_slug_gets_the_id():
    m = match(1, [node(10, "Silva", 3), node(11, "Silva", 2)], [], 5)
    assert player_slugs([m]) == {10: "silva-10", 11: "silva-11", 99: "rival"}


def test_share_is_over_the_games_played():
    # player 10 plays both games, player 11 only the second
    m1 = match(1, [node(10, "Ana", 10)], [], 10)
    m2 = match(2, [node(10, "Ana", 10), node(11, "Bia", 30)], [{"from": 11, "to": 10, "n": 30}], 40)
    pages = build_players([m1, m2], {1: (1, "G"), 2: (2, "G")}, min_pair=3)
    assert pages["ana"]["summary"]["share"] == 40.0  # 20 of 50
    assert pages["bia"]["summary"]["share"] == 75.0  # 30 of 40, not 30 of 50
    assert pages["bia"]["summary"]["teamRank"] == 1 and pages["ana"]["summary"]["teamRank"] == 2
    assert pages["ana"]["from"] == [{"playerId": 11, "name": "Bia", "slug": "bia", "n": 30}]
    assert pages["ana"]["games"][1]["partner"]["name"] == "Bia"
