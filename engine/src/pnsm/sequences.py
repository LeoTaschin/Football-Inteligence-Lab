"""Goal replays (CLAUDE.md 5.7): the ball path of the possession that ended in a goal.

Only the scoring team's events are used: the opponent's are in the opposite frame.
Times are seconds relative to the first event of the team in the possession.
"""

from __future__ import annotations

import math
from collections.abc import Callable

from pnsm.labels import LabelTarget, place_labels

MIN_CARRY_SECONDS = 0.1  # shorter carries are just the touch that controls the ball
MIN_CARRY_YARDS = 0.5
LONG_CARRY_YARDS = 12.0  # a carry this long gets its own narrated step
LONG_PASS_YARDS = 25.0
BACK_PASS_YARDS = 5.0
REPLAY_PITCH_PX = 840.0  # replay pitch width in the design
TOUCH_RADIUS_PX = 15.0

OPPONENT_ON_BALL = {"Pass", "Carry", "Ball Receipt*", "Dribble", "Shot"}

SHOT_OUTCOMES = {
    "Goal": "gol", "Saved": "defendido", "Blocked": "bloqueado", "Off T": "para fora",
    "Post": "na trave", "Wayward": "sem direção", "Saved Off Target": "defendido",
    "Saved to Post": "defendido na trave",
}

COUNT_WORDS = {2:"duas", 3: "três", 4: "quatro", 5: "cinco", 6: "seis"}


def _seconds(timestamp: str) -> float:
    h, m, s = timestamp.split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


def _dist(a: list[float], b: list[float]) -> float:
    return math.hypot(b[0] - a[0], b[1] - a[1])


def _side(y: float) -> str:
    # attacking to the right, y = 0 is the left touchline
    if y < 80 / 3:
        return "pela esquerda"
    if y > 160 / 3:
        return "pela direita"
    return "pelo meio"


def _r2(v: float) -> float:
    return round(float(v), 2)


def _carry_direction(start: list[float], end: list[float]) -> str:
    if abs(end[1] - 40) < abs(start[1] - 40) - 5:
        return "para o meio"
    return _side(end[1])


def goal_sequences(events: list[dict], team_id: int, name_of: Callable[[int], str],
                   num_of: Callable[[int], int | None], periods: tuple[int, ...] = (1, 2)) -> list[dict]:
    goals = [e for e in events if e["type"]["name"] == "Shot" and e["team"]["id"] == team_id
             and e["period"] in periods and e["shot"]["outcome"]["name"] == "Goal"]
    return [_sequence(events, goal, name_of, num_of) for goal in sorted(goals, key=lambda e: e["index"])]


def _sequence(events: list[dict], goal: dict, name_of, num_of) -> dict:
    team_id = goal["team"]["id"]
    possession = sorted((e for e in events if e.get("possession") == goal["possession"]
                         and e["period"] == goal["period"] and e["index"] <= goal["index"]),
                        key=lambda e: e["index"])
    # the possession id does not always change when the opponent loses the ball
    # (final, 36': Clodoaldo's back-heel), so start after the opponent's last touch
    last_opponent_touch = max((e["index"] for e in possession
                               if e["team"]["id"] != team_id and e["type"]["name"] in OPPONENT_ON_BALL), default=-1)
    possession = [e for e in possession if e["team"]["id"] == team_id and e["index"] > last_opponent_touch]
    t0 = _seconds(possession[0]["timestamp"])

    def t(e: dict) -> float:
        return _r2(_seconds(e["timestamp"]) - t0)

    segments, touches, steps = [], [], []
    dribbles: list[dict] = []  # pending group of completed dribbles by the same player

    def flush_dribbles(end_y: float | None) -> None:
        if not dribbles:
            return
        n = len(dribbles)
        who = name_of(dribbles[0]["player"]["id"])
        text = f"{who} dribla um adversário" if n == 1 else f"{who} dribla {COUNT_WORDS.get(n, n)} vezes"
        if end_y is not None:
            text += f" e conduz {_side(end_y)}"
        steps.append({"t": t(dribbles[0]), "text": text})
        dribbles.clear()

    last_carry_end: list[float] | None = None
    for e in possession:
        kind = e["type"]["name"]
        pid = e["player"]["id"] if e.get("player") else None
        loc = e.get("location")

        if dribbles and (pid != dribbles[0]["player"]["id"] or kind in ("Pass", "Shot")):
            flush_dribbles(last_carry_end[1] if last_carry_end else None)

        if kind in ("Ball Recovery", "Ball Receipt*") or (kind in ("Pass", "Carry", "Shot") and not touches):
            if loc and (not touches or touches[-1]["playerId"] != pid or kind != touches[-1]["kind"]):
                touches.append({"t": t(e), "playerId": pid, "num": num_of(pid), "name": name_of(pid),
                                "at": [_r2(loc[0]), _r2(loc[1])], "kind": kind})
            if kind == "Ball Recovery":
                half = "no próprio campo" if loc and loc[0] < 60 else "no campo de ataque"
                text = f"{name_of(pid)} recupera a bola {half}"
                if not steps or steps[-1]["text"] != text:
                    steps.append({"t": t(e), "text": text})

        if kind == "Carry":
            end = e["carry"]["end_location"]
            if (e.get("duration") or 0) < MIN_CARRY_SECONDS or _dist(loc, end) < MIN_CARRY_YARDS:
                continue
            segments.append({"t": t(e), "d": _r2(e["duration"]), "from": [_r2(loc[0]), _r2(loc[1])],
                             "to": [_r2(end[0]), _r2(end[1])], "kind": "carry"})
            last_carry_end = end
            if not dribbles and _dist(loc, end) >= LONG_CARRY_YARDS:
                steps.append({"t": t(e), "text": f"{name_of(pid)} conduz {_carry_direction(loc, end)}"})
        elif kind == "Dribble" and (e["dribble"].get("outcome") or {}).get("name") == "Complete":
            dribbles.append(e)
            last_carry_end = None
        elif kind == "Pass":
            end = e["pass"]["end_location"]
            segments.append({"t": t(e), "d": _r2(e.get("duration") or 0), "from": [_r2(loc[0]), _r2(loc[1])],
                             "to": [_r2(end[0]), _r2(end[1])], "kind": "pass"})
            recipient = e["pass"].get("recipient")
            steps.append({"t": t(e), "text": _pass_text(name_of(pid), name_of(recipient["id"]) if recipient else None,
                                                        loc, end)})
        elif kind == "Shot":
            end = e["shot"]["end_location"]
            segments.append({"t": t(e), "d": _r2(e.get("duration") or 0), "from": [_r2(loc[0]), _r2(loc[1])],
                             "to": [_r2(end[0]), _r2(end[1])], "kind": "shot"})
            head = (e["shot"].get("body_part") or {}).get("name") == "Head"
            outcome = e["shot"]["outcome"]["name"]
            steps.append({"t": t(e), "text": f"{name_of(pid)} {'cabeceia' if head else 'finaliza'}: "
                                             f"{SHOT_OUTCOMES.get(outcome, outcome.lower())}"})

    sides = place_labels(
        [LabelTarget(i, tc["at"][0], tc["at"][1], TOUCH_RADIUS_PX, tc["name"]) for i, tc in enumerate(touches)],
        width_px=REPLAY_PITCH_PX,
    )
    for i, tc in enumerate(touches):
        tc["label"] = sides[i]
        del tc["kind"]

    shot = segments[-1]
    passes = [s for s in segments if s["kind"] == "pass"]
    return {
        "team": goal["team"]["name"],
        "minute": goal["minute"],
        "scorerId": goal["player"]["id"],
        "scorer": name_of(goal["player"]["id"]),
        "duration": _r2(shot["t"] + shot["d"]),
        "passes": len(passes),
        "players": len({tc["playerId"] for tc in touches}),
        "segments": segments,
        "touches": touches,
        "steps": steps,
    }


def _pass_text(passer: str, recipient: str | None, start: list[float], end: list[float]) -> str:
    if recipient is None:
        return f"{passer} passa {_side(end[1])}"
    if _dist(start, end) >= LONG_PASS_YARDS and end[0] > start[0]:
        return f"{passer} lança {recipient} {_side(end[1])}"
    if end[0] < start[0] - BACK_PASS_YARDS:
        return f"{passer} recua para {recipient}"
    return f"{passer} → {recipient}"
