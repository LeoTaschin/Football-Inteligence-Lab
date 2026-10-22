"""Player pages (CLAUDE.md 5.10): one JSON per player with a node in any match of the collection.

Built from the exported match data (the same numbers the match page shows), aggregated by
``playerId``.
"""

from __future__ import annotations

from collections import defaultdict

from pnsm import names

TOP_PARTNERS = 5


def _r(v: float, digits: int = 1) -> float:
    return round(float(v), digits)


def player_slugs(matches: list[dict]) -> dict[int, str]:
    """``{playerId: slug}``; a slug two players would share gets the id appended to both."""
    display = {n["playerId"]: n["name"] for m in matches for t in m["teams"] for n in t["nodes"]}
    taken: dict[str, list[int]] = defaultdict(list)
    for pid, name in display.items():
        taken[names.slug(name)].append(pid)
    return {pid: (s if len(ids) == 1 else f"{s}-{pid}") for s, ids in taken.items() for pid in ids}


def build_players(matches: list[dict], order: dict[int, tuple[int, str]], min_pair: int) -> dict[str, dict]:
    """``{slug: player page}``. ``order`` maps match id → (order in the collection, stage)."""
    slugs = player_slugs(matches)
    games: dict[int, list[dict]] = defaultdict(list)
    to: dict[int, dict[int, int]] = defaultdict(lambda: defaultdict(int))
    frm: dict[int, dict[int, int]] = defaultdict(lambda: defaultdict(int))
    info: dict[int, dict] = {}

    for m in matches:
        mid = m["match"]["id"]
        for ti, team in enumerate(m["teams"]):
            opp = m["teams"][1 - ti]
            score = m["match"]["score"] if ti == 0 else m["match"]["score"][::-1]
            pairs = team["pairs"]
            mini = {
                "nodes": [{"playerId": n["playerId"], "num": n["num"], "x": n["ball"]["x"], "y": n["ball"]["y"],
                           "passes": n["passes"]} for n in team["nodes"]],
                "edges": [{"a": p["a"], "b": p["b"], "n": p["n"]} for p in pairs if p["n"] >= min_pair],
            }
            name_of = {n["playerId"]: n["name"] for n in team["nodes"]}
            for e in team["edges"]:
                to[e["from"]][e["to"]] += e["n"]
                frm[e["to"]][e["from"]] += e["n"]
            for node in team["nodes"]:
                pid = node["playerId"]
                info.setdefault(pid, {"name": node["name"], "num": node["num"], "position": node["position"],
                                      "teamId": team["teamId"], "team": team["displayName"], "teamName": team["name"],
                                      "article": team["article"], "colors": team["colors"]})
                # pairs come sorted by n: the first one with the player is his most used
                top = next((p for p in pairs if pid in (p["a"], p["b"])), None)
                partner = None
                if top:
                    other = top["b"] if top["a"] == pid else top["a"]
                    partner = {"playerId": other, "name": name_of[other], "slug": slugs[other], "n": top["n"]}
                games[pid].append({
                    "matchId": mid,
                    "order": order[mid][0],
                    "stage": order[mid][1],
                    "opponent": opp["displayName"],
                    "opponentArticle": opp["article"],
                    "score": score,
                    "passes": node["passes"],
                    "received": node["received"],
                    "teamCompleted": team["passes"]["completed"],
                    "rank": 1 + sum(1 for n in team["nodes"] if n["passes"] > node["passes"]),
                    "partner": partner,
                    "sub": node["sub"],
                    "positionFrom": node["positionFrom"],
                    "ball": node["ball"],
                    "def": node["def"],
                    "shift": node["shift"],
                    "mini": mini,
                })

    totals = {pid: sum(g["passes"] for g in gs) for pid, gs in games.items()}
    scale = {"maxPasses": max(n["passes"] for m in matches for t in m["teams"] for n in t["nodes"]),
             "maxPair": max((p["n"] for m in matches for t in m["teams"] for p in t["pairs"]), default=1)}

    def partners(counts: dict[int, int]) -> list[dict]:
        ranked = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:TOP_PARTNERS]
        return [{"playerId": pid, "name": info[pid]["name"], "slug": slugs[pid], "n": n} for pid, n in ranked]

    pages = {}
    for pid, gs in games.items():
        gs.sort(key=lambda g: g["order"])
        p = info[pid]
        passes, team_completed = totals[pid], sum(g["teamCompleted"] for g in gs)
        shifts = [g["shift"] for g in gs if g["shift"] is not None]
        mates = [q for q, i in info.items() if i["teamId"] == p["teamId"]]
        pages[slugs[pid]] = {
            "playerId": pid,
            "slug": slugs[pid],
            **p,
            "summary": {
                "games": len(gs),
                "passes": passes,
                "received": sum(g["received"] for g in gs),
                "teamCompleted": team_completed,
                "share": _r(100 * passes / team_completed) if team_completed else None,
                "teamRank": 1 + sum(1 for q in mates if totals[q] > passes),
                "topPasserGames": sum(1 for g in gs if g["rank"] == 1),
                "avgShift": _r(sum(shifts) / len(shifts)) if shifts else None,
            },
            "to": partners(to[pid]),
            "from": partners(frm[pid]),
            "scale": scale,
            "games": gs,
        }
    return pages


def player_list(pages: dict[str, dict]) -> list[dict]:
    """Everyone with a page (the players list and the links): team by team, most passes first."""
    rows = [{"playerId": p["playerId"], "slug": p["slug"], "name": p["name"], "num": p["num"], "position": p["position"],
             "team": p["team"], "teamName": p["teamName"], "games": p["summary"]["games"],
             "passes": p["summary"]["passes"], "received": p["summary"]["received"], "share": p["summary"]["share"],
             # came on as a substitute in at least one match
             "substitute": any(g["sub"] is not None and g["sub"]["type"] == "in" for g in p["games"])}
            for p in pages.values()]
    return sorted(rows, key=lambda r: (r["teamName"], -r["passes"], r["playerId"]))


def team_list(players: list[dict], matches: list[dict], rows: list[dict], team: str) -> list[dict]:
    """One entry per team of the players list: the analysed team first, then opponents in match order.

    ``rows`` are the collection's match rows (order, stage, score from the analysed team's side).
    Ties for the top passer / receiver go to the smaller ``playerId``.
    """
    colors = {t["name"]: t["colors"] for m in matches for t in m["teams"]}
    display = {t["name"]: (t["displayName"], t["article"]) for m in matches for t in m["teams"]}
    by_opp = {r["opponentName"]: r for r in rows}
    names_in_order = [team] + [r["opponentName"] for r in rows]
    out = []
    for name in names_in_order:
        ps = [p for p in players if p["teamName"] == name]
        top = lambda key: min(ps, key=lambda p: (-p[key], p["playerId"]))["playerId"]
        r = by_opp.get(name)
        out.append({
            "teamName": name,
            "team": display[name][0],
            "article": display[name][1],
            "colors": colors[name],
            "players": len(ps),
            "completed": sum(p["passes"] for p in ps),
            "topPasser": top("passes"),
            "topReceiver": top("received"),
            "allGames": sum(1 for p in ps if p["games"] == len(rows)) if name == team else None,
            "match": None if r is None else {"id": r["id"], "order": r["order"], "stage": r["stage"], "score": r["score"]},
        })
    return out
