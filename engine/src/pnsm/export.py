"""Write the site JSON (CLAUDE.md section 6): index, collection and one file per match.

Every number the site shows comes from here. The export validates each match and
stops on the first failure, writing nothing.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from pnsm import load, metrics, names, transform, validate
from pnsm.config import CollectionConfig
from pnsm.labels import LabelTarget, node_radius_px, place_labels
from pnsm.sequences import goal_sequences

YARDS_TO_METERS = 0.9144
LOW_DEF_SAMPLE = 5  # fewer defensive actions than this: the "sem bola" position is flagged
TOP_PASSERS = 6
TOP_PAIRS = 5
SOURCE = "StatsBomb Open Data"


def _r(v: float, digits: int = 2) -> float:
    return round(float(v), digits)


# --- match --------------------------------------------------------------------------

def build_match(meta: dict, events: list[dict], lineups: list[dict], cfg: CollectionConfig) -> dict:
    home, away = meta["home_team"], meta["away_team"]
    sides = [(home["home_team_id"], home["home_team_name"]), (away["away_team_id"], away["away_team_name"])]
    players = {t["team_id"]: names.players_from_lineup(t) for t in lineups}
    table = transform.passes_table(events)

    raw = []
    for team_id, team_name in sides:
        result = transform.eligible_passes(table, team_id, cfg.periods)
        raw.append((team_id, team_name, result, metrics.network_nodes(result.passes)))
    # same scale for both teams: fair visual comparison
    max_passes = max(int(nodes.passes.max()) for *_, nodes in raw if not nodes.empty)

    teams = [
        _build_team(team_id, team_name, result, nodes, events, players[team_id], cfg, max_passes)
        for team_id, team_name, result, nodes in raw
    ]

    def name_of(team_id):
        return lambda pid: players[team_id][pid].name if pid in players[team_id] else str(pid)

    def num_of(team_id):
        return lambda pid: players[team_id][pid].num if pid in players[team_id] else None

    goals = []
    for team_id, team_name in sides:
        for goal in goal_sequences(events, team_id, name_of(team_id), num_of(team_id), cfg.periods):
            goals.append({"teamId": team_id, **goal})
    goals.sort(key=lambda g: g["minute"])

    data = {
        "match": {
            "id": meta["match_id"],
            "date": meta["match_date"],
            "stage": names.stage_pt(meta["competition_stage"]["name"]),
            "competition": meta["competition"]["competition_name"],
            "season": meta["season"]["season_name"],
            "stadium": names.stadium_pt((meta.get("stadium") or {}).get("name")),
            "home": sides[0][1],
            "away": sides[1][1],
            "score": [meta["home_score"], meta["away_score"]],
        },
        "periods": sorted({e["period"] for e in events if e["period"] in cfg.periods}),
        "scale": {
            "maxPasses": max_passes,
            "maxPair": max((p["n"] for t in teams for p in t["pairs"]), default=1),
            "maxDirected": max((e["n"] for t in teams for e in t["edges"]), default=1),
        },
        "teams": teams,
        "goals": goals,
    }
    data["validation"] = validate.check_match(data, events, cfg.periods)
    return data


def _build_team(team_id: int, team_name: str, result: transform.PassFilterResult, nodes: pd.DataFrame,
                events: list[dict], players: dict[int, names.Player], cfg: CollectionConfig, max_passes: int) -> dict:
    edges = metrics.directed_edges(result.passes)
    pairs = metrics.pair_totals(edges)
    actions = transform.defensive_actions_table(events, team_id, cfg.defensive_actions, cfg.periods)
    defensive = metrics.defensive_positions(actions)
    shots = metrics.shot_summary(transform.shots_table(events, team_id, cfg.periods))
    subs = metrics.substitutions(events, team_id, cfg.periods)

    sub_info: dict[int, dict] = {}
    for s in subs:
        sub_info[s.out_id] = {"type": "out", "minute": s.minute, "with": s.in_id}
        sub_info[s.in_id] = {"type": "in", "minute": s.minute, "with": s.out_id}

    sides = place_labels([
        LabelTarget(pid, row.x, row.y, node_radius_px(row.passes, max_passes), players[pid].name)
        for pid, row in nodes.iterrows()
    ])

    node_list = []
    for pid, row in nodes.iterrows():
        player = players[pid]
        d = defensive.loc[pid] if pid in defensive.index else None
        node_list.append({
            "playerId": int(pid),
            "num": player.num,
            "name": player.name,
            "position": player.position,
            "ball": {"x": _r(row.x), "y": _r(row.y)},
            "positionFrom": row.position_from,
            "def": None if d is None else {"x": _r(d.x), "y": _r(d.y), "n": int(d.n), "lowSample": bool(d.n < LOW_DEF_SAMPLE)},
            "shift": None if d is None else _r((d.x - row.x) * YARDS_TO_METERS, 1),
            "passes": int(row.passes),
            "received": int(row.received),
            "sub": sub_info.get(int(pid)),
            "label": sides[pid],
        })

    outfield = [n for n in node_list if n["position"] != names.position_pt("Goalkeeper") and n["def"] is not None]
    phase = None
    if outfield:
        ball_h = sum(n["ball"]["x"] for n in outfield) / len(outfield)
        def_h = sum(n["def"]["x"] for n in outfield) / len(outfield)
        phase = {"ballHeight": _r(ball_h), "defHeight": _r(def_h), "shiftMeters": _r((def_h - ball_h) * YARDS_TO_METERS, 1)}

    return {
        "teamId": team_id,
        "name": team_name,
        "displayName": names.team_pt(team_name),
        "colors": names.team_colors(team_name),
        "passes": {
            "attempted": result.attempted,
            "completed": len(result.passes),
            "excluded": {"period": result.period, "incomplete": result.incomplete,
                         "noRecipient": result.no_recipient, "noLocation": result.no_location},
        },
        "nodes": node_list,
        "edges": [{"from": int(e.from_id), "to": int(e.to_id), "n": int(e.n)} for e in edges.itertuples()],
        "pairs": [{"a": int(p.first_id), "b": int(p.second_id), "forward": int(p.forward),
                   "backward": int(p.backward), "n": int(p.n)} for p in pairs.itertuples()],
        "substitutions": [{"minute": s.minute, "out": s.out_id, "in": s.in_id, "reason": s.reason} for s in subs],
        "shots": {"count": shots.count, "goals": shots.goals, "xg": _r(shots.xg), "xgCoverage": [shots.with_xg, shots.count]},
        "phase": phase,
    }


# --- collection ---------------------------------------------------------------------

def build_collection(cfg: CollectionConfig, matches: list[dict]) -> dict:
    rows = []
    passers: dict[int, dict] = {}
    campaign_edges: list[pd.DataFrame] = []

    for order, data in enumerate(matches, start=1):
        i = [t["name"] for t in data["teams"]].index(cfg.team)
        team, opp = data["teams"][i], data["teams"][1 - i]
        goals_for, goals_against = data["match"]["score"][i], data["match"]["score"][1 - i]
        by_id = {n["playerId"]: n for n in team["nodes"]}

        for n in team["nodes"]:
            entry = passers.setdefault(n["playerId"], {"name": n["name"], "n": 0})
            entry["n"] += n["passes"]
        campaign_edges.append(pd.DataFrame(team["edges"]).rename(columns={"from": "from_id", "to": "to_id"}))

        top = team["pairs"][0]
        rows.append({
            "id": data["match"]["id"],
            "order": order,
            "stage": data["match"]["stage"],
            "opponent": opp["displayName"],
            "opponentName": opp["name"],
            "score": [goals_for, goals_against],
            "completed": team["passes"]["completed"],
            "attempted": team["passes"]["attempted"],
            "opponentCompleted": opp["passes"]["completed"],
            "xg": team["shots"]["xg"],
            "opponentXg": opp["shots"]["xg"],
            "topPair": {"ids": [top["a"], top["b"]], "names": [by_id[top["a"]]["name"], by_id[top["b"]]["name"]], "n": top["n"]},
            "mini": {
                "nodes": [{"playerId": n["playerId"], "num": n["num"], "x": n["ball"]["x"], "y": n["ball"]["y"],
                           "passes": n["passes"]} for n in team["nodes"]],
                "edges": [{"a": p["a"], "b": p["b"], "n": p["n"]} for p in team["pairs"] if p["n"] >= cfg.min_pair_passes],
            },
            "note": None,
        })

    _add_notes(rows, cfg.team)

    edges = pd.concat(campaign_edges).groupby(["from_id", "to_id"], as_index=False).n.sum()
    pairs = metrics.pair_totals(edges).head(TOP_PAIRS)
    top_passers = sorted(passers.items(), key=lambda kv: -kv[1]["n"])[:TOP_PASSERS]

    completed = sum(r["completed"] for r in rows)
    attempted = sum(r["attempted"] for r in rows)
    return {
        "id": cfg.collection,
        "title": cfg.title,
        "team": cfg.team,
        "displayName": names.team_pt(cfg.team),
        "colors": names.team_colors(cfg.team),
        "summary": {
            "played": len(rows),
            "wins": sum(r["score"][0] > r["score"][1] for r in rows),
            "draws": sum(r["score"][0] == r["score"][1] for r in rows),
            "losses": sum(r["score"][0] < r["score"][1] for r in rows),
            "goalsFor": sum(r["score"][0] for r in rows),
            "goalsAgainst": sum(r["score"][1] for r in rows),
            "completed": completed,
            "attempted": attempted,
            "accuracy": _r(100 * completed / attempted, 1) if attempted else None,
            "xgFor": _r(sum(r["xg"] for r in rows)),
            "xgAgainst": _r(sum(r["opponentXg"] for r in rows)),
            "morePassesThanOpponent": sum(r["completed"] > r["opponentCompleted"] for r in rows),
        },
        "matches": rows,
        "topPassers": [{"playerId": pid, "name": p["name"], "n": p["n"]} for pid, p in top_passers],
        "topPairs": [{"ids": [int(p.first_id), int(p.second_id)],
                      "names": [passers[p.first_id]["name"], passers[p.second_id]["name"]], "n": int(p.n)}
                     for p in pairs.itertuples()],
    }


def _add_notes(rows: list[dict], team: str) -> None:
    """Card notes from simple rules, at most one per match, first rule wins. Never written by hand."""
    art, name = names.team_article(team), names.team_pt(team)
    of_team = {"o": "do", "a": "da"}[art]

    def note(row: dict, text: str) -> None:
        if row["note"] is None:
            row["note"] = text

    won_with_less_xg = [r for r in rows if r["score"][0] > r["score"][1] and r["xg"] < r["opponentXg"]]
    if len(won_with_less_xg) == 1:
        note(won_with_less_xg[0], f"Único jogo em que {art} {name} criou menos xG que o adversário, e venceu.")

    if len(rows) > 1:
        most = max(rows, key=lambda r: r["completed"])
        note(most, f"Jogo com mais passes completos {of_team} {name} na campanha.")

        biggest = max(rows, key=lambda r: r["completed"] - r["opponentCompleted"])
        diff = biggest["completed"] - biggest["opponentCompleted"]
        if diff > 0:
            opp_art = names.team_article(biggest["opponentName"])
            note(biggest, f"Maior diferença de passes da campanha: {diff} a mais que {opp_art} {biggest['opponent']}.")


def build_index(cfg: CollectionConfig, match_ids: list[int]) -> dict:
    return {
        "generatedAt": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "source": SOURCE,
        "collections": [{
            "id": cfg.collection,
            "title": cfg.title,
            "competitionId": cfg.competition_id,
            "seasonId": cfg.season_id,
            "team": cfg.team,
            "matches": match_ids,
        }],
    }


# --- write --------------------------------------------------------------------------

def export_collection(cfg: CollectionConfig, cache_dir: Path = load.DEFAULT_CACHE_DIR) -> list[Path]:
    match_ids = load.fetch_season(cfg.competition_id, cfg.season_id, team=cfg.team, cache_dir=cache_dir)
    matches = []
    for match_id in match_ids:
        meta = load.find_match(match_id, cfg.competition_id, cfg.season_id, cache_dir)
        matches.append(build_match(meta, load.load_events(match_id, cache_dir), load.load_lineups(match_id, cache_dir), cfg))

    # everything validated: only now touch the output directory
    out = cfg.output_dir
    written = [_write(out / "matches" / f"{m['match']['id']}.json", m) for m in matches]
    written.append(_write(out / "collections" / f"{cfg.collection}.json", build_collection(cfg, matches)))
    written.append(_write(out / "index.json", build_index(cfg, match_ids)))
    return written


def _write(path: Path, data: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return path
