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

        team_shots = shots_by_team.get(tid, [])
        check("shotCount", team["shots"]["count"] == len(team_shots), f"{label}: chutes exportados ≠ eventos Shot")
        shot_goals = sum(1 for s in team_shots if s["shot"]["outcome"]["name"] == "Goal")
        check("shotGoals", team["shots"]["goals"] == shot_goals, f"{label}: gols ≠ Shot com outcome Goal")

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
