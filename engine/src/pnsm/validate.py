"""Consistency checks run by the export (CLAUDE.md section 8). Any failure blocks the export."""

from __future__ import annotations


class ValidationError(Exception):
    pass


def check_match(data: dict, events: list[dict], periods: tuple[int, ...]) -> dict[str, bool]:
    """Run every check on an exported match. Returns the results; raises if any fails."""
    results: dict[str, bool] = {}
    failures: list[str] = []

    def check(name: str, ok: bool, detail: str) -> None:
        results[name] = results.get(name, True) and ok
        if not ok:
            failures.append(f"{name}: {detail}")

    shots_by_team: dict[int, list[dict]] = {}
    own_goals_for: dict[int, int] = {}
    for e in events:
        if e["type"]["name"] == "Shot" and e["period"] in periods:
            shots_by_team.setdefault(e["team"]["id"], []).append(e)
        if e["type"]["name"] == "Own Goal For" and e["period"] != 5:
            own_goals_for[e["team"]["id"]] = own_goals_for.get(e["team"]["id"], 0) + 1

    for team in data["teams"]:
        tid, label = team["teamId"], team["name"]
        completed = team["passes"]["completed"]
        excluded = team["passes"]["excluded"]
        node_ids = {n["playerId"] for n in team["nodes"]}

        check("edgeSumEqualsCompleted", sum(e["n"] for e in team["edges"]) == completed,
              f"{label}: soma das conexões ≠ {completed}")
        check("nodeSumEqualsCompleted", sum(n["passes"] for n in team["nodes"]) == completed,
              f"{label}: soma dos nós ≠ {completed}")
        check("excludedAddUp",
              team["passes"]["attempted"] - excluded["incomplete"] - excluded["noRecipient"] - excluded["noLocation"] == completed,
              f"{label}: tentados − excluídos ≠ completos")
        check("edgesHaveNodes", all(e["from"] in node_ids and e["to"] in node_ids for e in team["edges"]),
              f"{label}: conexão com jogador sem nó")
        check("pairSumEqualsCompleted", sum(p["n"] for p in team["pairs"]) == completed,
              f"{label}: soma dos pares ≠ {completed}")

        cuts = team["cuts"]
        for key, cut in cuts.items():
            ids = {n["playerId"] for n in cut["nodes"]}
            n = cut["completed"]
            check("cutSumsAdd", sum(e["n"] for e in cut["edges"]) == n and sum(x["passes"] for x in cut["nodes"]) == n
                  and sum(p["n"] for p in cut["pairs"]) == n, f"{label}/{key}: soma das conexões, nós ou pares ≠ {n}")
            check("cutEdgesHaveNodes", all(e["from"] in ids and e["to"] in ids for e in cut["edges"]),
                  f"{label}/{key}: conexão com jogador sem nó")
            check("cutNotLarger", n <= completed, f"{label}/{key}: recorte com mais passes que a partida inteira")
        # open play = full minus the set pieces it removed, in both periods
        check("openPlayAddsUp", cuts["openPlay"]["completed"] + sum(cuts["openPlay"]["removed"].values()) == completed,
              f"{label}: jogo aberto + bolas paradas ≠ {completed}")
        check("firstSubOpenAddsUp",
              cuts["firstSubOpen"]["completed"] + sum(cuts["firstSubOpen"]["removed"].values()) == cuts["firstSub"]["completed"],
              f"{label}: até a 1ª sub, jogo aberto + bolas paradas ≠ recorte")
        check("noSubMeansSame", bool(team["substitutions"]) or cuts["firstSub"]["sameAsFull"],
              f"{label}: sem substituição mas recorte diferente da partida inteira")

        team_shots = shots_by_team.get(tid, [])
        check("shotCount", team["shots"]["count"] == len(team_shots), f"{label}: chutes exportados ≠ eventos Shot")
        shot_goals = sum(1 for s in team_shots if s["shot"]["outcome"]["name"] == "Goal")
        check("shotGoals", team["shots"]["goals"] == shot_goals, f"{label}: gols ≠ Shot com outcome Goal")
        items = team["shots"]["items"]
        check("shotItemsMatchCount", len(items) == team["shots"]["count"], f"{label}: lista de chutes ≠ contagem")
        check("shotItemsGoals", sum(s["result"] == "goal" for s in items) == shot_goals,
              f"{label}: chutes marcados como gol ≠ Shot com outcome Goal")
        with_xg = [s["xg"] for s in items if s["xg"] is not None]
        check("shotItemsXg", len(with_xg) == team["shots"]["xgCoverage"][0]
              and abs(sum(with_xg) - team["shots"]["xg"]) < 0.01 * max(1, len(with_xg)),
              f"{label}: xG da lista ≠ total (ou cobertura)")

    score = data["match"]["score"]
    for i, team in enumerate(data["teams"]):
        all_shot_goals = sum(1 for e in events if e["type"]["name"] == "Shot" and e["period"] != 5
                             and e["team"]["id"] == team["teamId"] and e["shot"]["outcome"]["name"] == "Goal")
        check("scoreMatchesEvents", all_shot_goals + own_goals_for.get(team["teamId"], 0) == score[i],
              f"{team['name']}: gols nos eventos ≠ placar {score[i]}")

    team_ids = {t["teamId"] for t in data["teams"]}
    for goal in data["goals"]:
        times = [s["t"] for s in goal["segments"]]
        check("replayOrdered", times == sorted(times), f"gol {goal['minute']}′: segmentos fora de ordem")
        check("replayEndsWithShot", bool(goal["segments"]) and goal["segments"][-1]["kind"] == "shot",
              f"gol {goal['minute']}′: último segmento não é o chute")
        check("noForeignEvents", goal["teamId"] in team_ids, f"gol {goal['minute']}′: equipe desconhecida")

    results.setdefault("noForeignEvents", True)
    if failures:
        raise ValidationError(f"partida {data['match']['id']}:\n  " + "\n  ".join(failures))
    return results
