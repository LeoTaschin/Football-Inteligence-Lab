"""Typed tables built from raw StatsBomb events.

``passes_table`` only flattens the JSON: it keeps every Pass event, of both teams
and every period. The football rules (which passes enter the network) live in
``eligible_passes``.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

PITCH_LENGTH = 120.0
PITCH_WIDTH = 80.0

PASS_COLUMNS = [
    "event_id", "index", "period", "minute", "second", "possession",
    "team_id", "team", "player_id", "player",
    "x", "y", "end_x", "end_y",
    "recipient_id", "outcome", "pass_type",
]


def _xy(location: list | None) -> tuple[float | None, float | None]:
    if not location or len(location) < 2:
        return None, None
    return float(location[0]), float(location[1])


def _name(obj: dict | None) -> str | None:
    return obj["name"] if obj else None


def passes_table(events: list[dict]) -> pd.DataFrame:
    """One row per ``Pass`` event, with the raw values (missing stays missing).

    ``outcome`` is None when the JSON has no ``pass.outcome`` (StatsBomb: completed pass).
    """
    rows = []
    for e in events:
        if e["type"]["name"] != "Pass":
            continue
        p = e["pass"]
        x, y = _xy(e.get("location"))
        end_x, end_y = _xy(p.get("end_location"))
        recipient = p.get("recipient")
        rows.append({
            "event_id": e["id"],
            "index": e["index"],
            "period": e["period"],
            "minute": e["minute"],
            "second": e["second"],
            "possession": e.get("possession"),
            "team_id": e["team"]["id"],
            "team": e["team"]["name"],
            "player_id": e["player"]["id"] if e.get("player") else None,
            "player": _name(e.get("player")),
            "x": x, "y": y, "end_x": end_x, "end_y": end_y,
            "recipient_id": recipient["id"] if recipient else None,
            "outcome": _name(p.get("outcome")),
            "pass_type": _name(p.get("type")),
        })
    table = pd.DataFrame(rows, columns=PASS_COLUMNS)
    # nullable ints: a missing recipient stays <NA> instead of turning the column into floats
    return table.astype({"player_id": "Int64", "recipient_id": "Int64"})


@dataclass(frozen=True)
class PassFilterResult:
    """Passes that enter the network plus the count of excluded passes by reason.

    ``attempted`` = team passes inside the analysed periods.
    Invariant: ``attempted - incomplete - no_recipient - no_location == len(passes)``.
    """

    passes: pd.DataFrame
    attempted: int
    period: int
    incomplete: int
    no_recipient: int
    no_location: int


def eligible_passes(passes: pd.DataFrame, team_id: int, periods: tuple[int, ...] = (1, 2)) -> PassFilterResult:
    """Completed passes of ``team_id`` that enter the network (CLAUDE.md, section 5.1).

    Filters, applied in sequence (each excluded pass counts under ONE reason only):
      1. team: other teams' passes are dropped, not counted as excluded;
      2. period: ``period`` not in ``periods``          -> ``period``
      3. incomplete: ``outcome`` is not missing          -> ``incomplete``
      4. no recipient: ``recipient_id`` is missing       -> ``no_recipient``
      5. no valid location: ``x``/``y`` missing or outside 0..120 x 0..80 -> ``no_location``
    """
    team = passes[passes.team_id == team_id]

    in_periods = team.period.isin(periods)
    excluded_period = int((~in_periods).sum())
    kept = team[in_periods]
    attempted = len(kept)

    # each filter sees only what survived the previous one, so a pass is counted under one reason
    filters = {
        "incomplete": lambda d: d.outcome.isna(),
        "no_recipient": lambda d: d.recipient_id.notna(),
        "no_location": lambda d: d.x.between(0, PITCH_LENGTH) & d.y.between(0, PITCH_WIDTH),
    }
    excluded = {}
    for reason, keep_mask in filters.items():
        keep = keep_mask(kept)
        excluded[reason] = int((~keep).sum())
        kept = kept[keep]

    return PassFilterResult(
        passes=kept.reset_index(drop=True),
        attempted=attempted,
        period=excluded_period,
        **excluded,
    )
