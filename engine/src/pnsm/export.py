"""Write the site JSON (CLAUDE.md section 6): index, collection and one file per match.

Every number the site shows comes from here. The export validates each match and
stops on the first failure, writing nothing.
"""

from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from pnsm import load, metrics, names, players, transform, validate
from pnsm.config import CollectionConfig
from pnsm.labels import LabelTarget, node_radius_px, place_labels
from pnsm.sequences import goal_sequences

YARDS_TO_METERS = 0.9144
LOW_DEF_SAMPLE = 5  # fewer defensive actions than this: the "sem bola" position is flagged
TOP_PASSERS = 6
TOP_PAIRS = 5
TOP_CHANCES = 5
GOAL_CENTER = (120.0, 40.0)
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
    # one scale for both teams and every cut: the full network is the largest
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
            "country": names.country_pt(((meta.get("stadium") or {}).get("country") or {}).get("name")),
            "home": sides[0][1],
            "away": sides[1][1],
            "score": [meta["home_score"], meta["away_score"]],
        },
        "periods": sorted({e["period"] for e in events if e["period"] in cfg.periods}),
        "scale": {
            "maxPasses": max_passes,
            "maxPair": max((p["n"] for t in teams for p in t["pairs"]), default=1),
            "maxDirected": max((e["n"] for t in teams for e in t["edges"]), default=1),
            "shotsFromX": _shots_from_x(teams),
        },
        "teams": teams,
        "goals": goals,
    }
    data["validation"] = validate.check_match(data, events, cfg.periods)
    return data


def _network(passes: pd.DataFrame, nodes: pd.DataFrame, players: dict[int, names.Player],
             sub_info: dict[int, dict], max_passes: int) -> tuple[list[dict], list[dict], list[dict]]:
    """Nodes (without the "sem bola" fields), directed edges and pairs of one network."""
    edges = metrics.directed_edges(passes)
    pairs = metrics.pair_totals(edges)
    sides = place_labels([
        LabelTarget(pid, row.x, row.y, node_radius_px(row.passes, max_passes), players[pid].name)
        for pid, row in nodes.iterrows()
    ])
    node_list = [{
        "playerId": int(pid),
        "num": players[pid].num,
        "name": players[pid].name,
        "position": players[pid].position,
        "ball": {"x": _r(row.x), "y": _r(row.y)},
        "positionFrom": row.position_from,
        "passes": int(row.passes),
        "received": int(row.received),
        "sub": sub_info.get(int(pid)),
        "label": sides[pid],
    } for pid, row in nodes.iterrows()]
    edge_list = [{"from": int(e.from_id), "to": int(e.to_id), "n": int(e.n)} for e in edges.itertuples()]
    pair_list = [{"a": int(p.first_id), "b": int(p.second_id), "forward": int(p.forward),
                  "backward": int(p.backward), "n": int(p.n)} for p in pairs.itertuples()]
    return node_list, edge_list, pair_list


def _cuts(events: list[dict], team_id: int, passes: pd.DataFrame, full_nodes: pd.DataFrame,
          subs: list[metrics.Substitution], players: dict[int, names.Player], sub_info: dict[int, dict],
          max_passes: int) -> dict:
    """The three cuts besides the full network (CLAUDE.md 5.9)."""
    first_sub = transform.first_substitution_index(events, team_id)
    cuts = transform.network_cuts(passes, first_sub)
    removed = transform.removed_set_pieces(passes)
    removed_until_sub = transform.removed_set_pieces(cuts["firstSub"])
    cut_at = None if not subs else {"minute": subs[0].minute, "out": subs[0].out_id, "in": subs[0].in_id}

    out = {}
    for key in transform.CUTS[1:]:
        cut = cuts[key]
        nodes = metrics.network_nodes(cut)
        node_list, edge_list, pair_list = _network(cut, nodes, players, sub_info, max_passes)
        h = metrics.cut_highlights(full_nodes, nodes)
        out[key] = {
            "completed": len(cut),
            "sameAsFull": len(cut) == len(passes),
            "cutAt": cut_at if key in ("firstSub", "firstSubOpen") else None,
            "removed": {"openPlay": removed, "firstSubOpen": removed_until_sub}.get(key),
            "highlights": {
                "shift": None if h.shift_id is None else {"playerId": h.shift_id, "meters": h.shift_m},
                "drop": None if h.drop_id is None else {"playerId": h.drop_id, "from": h.drop_from, "to": h.drop_to},
            },
            "nodes": node_list,
            "edges": edge_list,
            "pairs": pair_list,
        }
    return out


def _build_team(team_id: int, team_name: str, result: transform.PassFilterResult, nodes: pd.DataFrame,
                events: list[dict], players: dict[int, names.Player], cfg: CollectionConfig, max_passes: int) -> dict:
    actions = transform.defensive_actions_table(events, team_id, cfg.defensive_actions, cfg.periods)
    defensive = metrics.defensive_positions(actions)
    shot_rows = transform.shots_table(events, team_id, cfg.periods)
    shots = metrics.shot_summary(shot_rows)
    shot_items = _shot_items(shot_rows, players)
    subs = metrics.substitutions(events, team_id, cfg.periods)

    sub_info: dict[int, dict] = {}
    for s in subs:
        sub_info[s.out_id] = {"type": "out", "minute": s.minute, "with": s.in_id}
        sub_info[s.in_id] = {"type": "in", "minute": s.minute, "with": s.out_id}

    node_list, edge_list, pair_list = _network(result.passes, nodes, players, sub_info, max_passes)
    for n in node_list:
        pid, row = n["playerId"], nodes.loc[n["playerId"]]
        d = defensive.loc[pid] if pid in defensive.index else None
        n["def"] = None if d is None else {"x": _r(d.x), "y": _r(d.y), "n": int(d.n), "lowSample": bool(d.n < LOW_DEF_SAMPLE)}
        n["shift"] = None if d is None else _r((d.x - row.x) * YARDS_TO_METERS, 1)

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
        "article": names.team_article(team_name),
        "colors": names.team_colors(team_name),
        "passes": {
            "attempted": result.attempted,
            "completed": len(result.passes),
            "excluded": {"period": result.period, "incomplete": result.incomplete,
                         "noRecipient": result.no_recipient, "noLocation": result.no_location},
        },
        "nodes": node_list,
        "edges": edge_list,
        "pairs": pair_list,
        "cuts": _cuts(events, team_id, result.passes, nodes, subs, players, sub_info, max_passes),
        "substitutions": [{"minute": s.minute, "out": s.out_id, "in": s.in_id, "reason": s.reason} for s in subs],
        "shots": {"count": shots.count, "goals": shots.goals, "xg": _r(shots.xg),
                  "xgPerShot": None if shots.mean_xg is None else _r(shots.mean_xg, 3),
                  "xgCoverage": [shots.with_xg, shots.count],
                  "items": shot_items, "top": _top_chances(shot_items)},
        "phase": phase,
    }


def _opt(v, digits: int = 2) -> float | None:
    """Round a value that may be missing; missing stays ``None`` (never 0)."""
    return None if v is None or pd.isna(v) else _r(v, digits)


def _shots_from_x(teams: list[dict]) -> int:
    """Where the shot map starts: half way (60), or further back in 5-yard steps if a shot needs it."""
    xs = [s["x"] for t in teams for s in t["shots"]["items"] if s["x"] is not None]
    lowest = min(xs, default=60.0) - 2  # room for the marker
    return int(min(60, (lowest // 5) * 5))


def _top_chances(items: list[dict]) -> list[int]:
    """Indices of the TOP_CHANCES shots with the highest xG; ties keep the earlier shot first."""
    ranked = sorted((i for i, s in enumerate(items) if s["xg"] is not None), key=lambda i: -items[i]["xg"])
    return ranked[:TOP_CHANCES]


def _shot_items(shot_rows: pd.DataFrame, players: dict[int, names.Player]) -> list[dict]:
    items = []
    for s in metrics.shot_list(shot_rows).itertuples():
        player = players.get(s.player_id)
        end = [_opt(s.end_x), _opt(s.end_y)] + ([] if pd.isna(s.end_z) else [_opt(s.end_z)])
        items.append({
            "period": int(s.period), "minute": int(s.minute), "second": int(s.second),
            "playerId": int(s.player_id),
            "name": player.name if player else s.player,
            "num": player.num if player else None,
            "x": _opt(s.x), "y": _opt(s.y),
            "distance": None if pd.isna(s.x) else _r(math.hypot(GOAL_CENTER[0] - s.x, GOAL_CENTER[1] - s.y) * YARDS_TO_METERS, 1),
            "end": None if end[0] is None else end,
            "outcome": s.outcome, "result": s.result,
            "xg": _opt(s.xg, 3),
            "shotType": s.shot_type_code, "setPiece": bool(s.set_piece),
            "bodyPart": s.body_part_code,
            "finish": metrics.shot_finish(s.result, s.x, s.y, None if pd.isna(s.end_x) else s.end_x,
                                          None if pd.isna(s.end_y) else s.end_y, None if pd.isna(s.end_z) else s.end_z),
        })
    return items


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
            entry = passers.setdefault(n["playerId"], {"name": n["name"], "n": 0, "played": set(), "positions": []})
            entry["n"] += n["passes"]
            entry["played"].add(data["match"]["id"])
            if n["position"]:
                entry["positions"].append(n["position"])
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
    countries = {m["match"]["country"] for m in matches if m["match"]["country"]}
    return {
        "id": cfg.collection,
        "title": cfg.title,
        "competition": matches[0]["match"]["competition"],
        "season": matches[0]["match"]["season"],
        "country": countries.pop() if len(countries) == 1 else None,
        "team": cfg.team,
        "displayName": names.team_pt(cfg.team),
        "article": names.team_article(cfg.team),
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
        "scale": {
            "maxPasses": max(n["passes"] for r in rows for n in r["mini"]["nodes"]),
            "maxPair": max((e["n"] for r in rows for e in r["mini"]["edges"]), default=1),
        },
        "matches": rows,
        # "missed": matches (opponent names) in which the player did not appear in the network
        "topPassers": [{"playerId": pid, "name": p["name"], "n": p["n"],
                        "position": max(set(p["positions"]), key=p["positions"].count) if p["positions"] else None,
                        "missed": [r["opponent"] for r in rows if r["id"] not in p["played"]]}
                       for pid, p in top_passers],
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

def build_files(cfg: CollectionConfig, cache_dir: Path = load.DEFAULT_CACHE_DIR) -> dict[Path, dict]:
    """Every site JSON of the collection, validated, keyed by its path relative to ``output_dir``."""
    match_ids = load.fetch_season(cfg.competition_id, cfg.season_id, team=cfg.team, cache_dir=cache_dir)
    matches = []
    for match_id in match_ids:
        meta = load.find_match(match_id, cfg.competition_id, cfg.season_id, cache_dir)
        matches.append(build_match(meta, load.load_events(match_id, cache_dir), load.load_lineups(match_id, cache_dir), cfg))

    files = {Path("matches") / f"{m['match']['id']}.json": m for m in matches}
    collection = build_collection(cfg, matches)
    order = {r["id"]: (r["order"], r["stage"]) for r in collection["matches"]}
    pages = players.build_players(matches, order, cfg.min_pair_passes)
    validate.check_players(pages, matches)
    slugs = {p["playerId"]: s for s, p in pages.items()}
    collection["players"] = players.player_list(pages)
    for t in collection["topPassers"]:
        t["slug"] = slugs[t["playerId"]]
    files[Path("collections") / f"{cfg.collection}.json"] = collection
    files.update({Path("players") / f"{s}.json": p for s, p in pages.items()})
    files[Path("index.json")] = build_index(cfg, match_ids)
    return files


def export_collection(cfg: CollectionConfig, cache_dir: Path = load.DEFAULT_CACHE_DIR) -> list[Path]:
    files = build_files(cfg, cache_dir)
    # everything validated: only now touch the output directory
    return [_write(cfg.output_dir / rel, data) for rel, data in files.items()]


VOLATILE_KEYS = {"generatedAt"}  # change on every run; not part of the data


def stale_files(cfg: CollectionConfig, cache_dir: Path = load.DEFAULT_CACHE_DIR) -> list[str]:
    """Committed JSON that differs from a fresh export (ignoring ``generatedAt``). Empty = up to date."""
    stale = []
    for rel, data in build_files(cfg, cache_dir).items():
        path = cfg.output_dir / rel
        if not path.exists():
            stale.append(f"{rel} (ausente)")
            continue
        committed = json.loads(path.read_text(encoding="utf-8"))
        if _strip(committed) != _strip(json.loads(json.dumps(data, ensure_ascii=False))):
            stale.append(str(rel))
    return stale


def _strip(data: dict) -> dict:
    return {k: v for k, v in data.items() if k not in VOLATILE_KEYS}


def _write(path: Path, data: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return path
