"""Pass network, shot and phase metrics (CLAUDE.md, section 5).

Every function receives tables already filtered by ``transform`` and aggregates by
``player_id``. Nothing here filters events again.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

YARDS_TO_METERS = 0.9144


def network_nodes(passes: pd.DataFrame) -> pd.DataFrame:
    """One row per player (index ``player_id``) with ``x``, ``y``, ``passes``, ``received``, ``position_from``.

    Position = median of the locations of the completed passes the player MADE.
    A player who only received (0 passes made) is placed at the median of the
    ``end_location`` of the passes he received and flagged ``position_from = "received"``.
    """
    made = passes.groupby("player_id").agg(x=("x", "median"), y=("y", "median"), passes=("event_id", "size"))
    made["position_from"] = "passes"

    received = passes.groupby("recipient_id").size().rename("received")
    only_received = passes[~passes.recipient_id.isin(made.index)]
    fallback = only_received.groupby("recipient_id").agg(x=("end_x", "median"), y=("end_y", "median"))
    fallback["passes"] = 0
    fallback["position_from"] = "received"

    nodes = pd.concat([made, fallback])
    nodes.index = nodes.index.astype(int).rename("player_id")
    nodes["received"] = received.reindex(nodes.index, fill_value=0).astype(int)
    nodes["passes"] = nodes.passes.astype(int)
    return nodes.sort_values(["passes", "received"], ascending=False)


def directed_edges(passes: pd.DataFrame) -> pd.DataFrame:
    """``from_id → to_id`` with the number of completed passes, most used first."""
    edges = passes.groupby(["player_id", "recipient_id"]).size().rename("n").reset_index()
    edges = edges.rename(columns={"player_id": "from_id", "recipient_id": "to_id"}).astype(int)
    return edges.sort_values(["n", "from_id", "to_id"], ascending=[False, True, True]).reset_index(drop=True)


def pair_totals(edges: pd.DataFrame) -> pd.DataFrame:
    """Undirected pairs: ``first_id`` is the player who passed more inside the pair.

    Columns: ``first_id``, ``second_id``, ``forward`` (first → second), ``backward``, ``n``.
    Ties keep the smaller ``player_id`` first so the order is deterministic.
    """
    counts = {(r.from_id, r.to_id): r.n for r in edges.itertuples()}
    rows = []
    for a, b in {tuple(sorted(k)) for k in counts}:
        ab, ba = counts.get((a, b), 0), counts.get((b, a), 0)
        first, second, forward, backward = (a, b, ab, ba) if ab >= ba else (b, a, ba, ab)
        rows.append({"first_id": first, "second_id": second, "forward": forward, "backward": backward, "n": ab + ba})
    pairs = pd.DataFrame(rows, columns=["first_id", "second_id", "forward", "backward", "n"])
    return pairs.sort_values(["n", "forward", "first_id", "second_id"], ascending=[False, False, True, True]).reset_index(drop=True)


MIN_PASSES_FOR_SHIFT = 5  # a median from fewer passes moves too easily to be a finding


@dataclass(frozen=True)
class CutHighlights:
    shift_id: int | None  # player whose position moves the most
    shift_m: float | None
    drop_id: int | None  # player who loses the most passes
    drop_from: int | None
    drop_to: int | None


def cut_highlights(full: pd.DataFrame, cut: pd.DataFrame) -> CutHighlights:
    """Compare a cut's nodes with the full network's (both from ``network_nodes``).

    Shift: distance between the two medians, only for players with >= MIN_PASSES_FOR_SHIFT
    passes in both. Drop: largest fall in passes made (a player missing from the cut has 0).
    Ties go to the smaller ``player_id``; ``None`` when nothing changes.
    """
    both = full.join(cut, how="inner", lsuffix="_full")
    both = both[(both.passes_full >= MIN_PASSES_FOR_SHIFT) & (both.passes >= MIN_PASSES_FOR_SHIFT)]
    dist = (((both.x - both.x_full) ** 2 + (both.y - both.y_full) ** 2) ** 0.5 * YARDS_TO_METERS).round(1)
    dist = dist[dist > 0].sort_index()
    shift_id = int(dist.idxmax()) if not dist.empty else None

    after = cut.passes.reindex(full.index, fill_value=0)
    fall = (full.passes - after).sort_index()
    fall = fall[fall > 0]
    drop_id = int(fall.idxmax()) if not fall.empty else None
    return CutHighlights(
        shift_id=shift_id, shift_m=float(dist.max()) if shift_id is not None else None,
        drop_id=drop_id,
        drop_from=int(full.passes[drop_id]) if drop_id is not None else None,
        drop_to=int(after[drop_id]) if drop_id is not None else None,
    )


def defensive_positions(actions: pd.DataFrame) -> pd.DataFrame:
    """Median location of each player's defensive actions (index ``player_id``) and how many there were."""
    positions = actions.groupby("player_id").agg(x=("x", "median"), y=("y", "median"), n=("event_id", "size"))
    positions.index = positions.index.astype(int)
    return positions


@dataclass(frozen=True)
class ShotSummary:
    count: int
    goals: int
    xg: float  # sum of the available values only
    with_xg: int  # coverage: ``with_xg`` of ``count`` shots have a provider xG

    @property
    def mean_xg(self) -> float | None:
        return self.xg / self.with_xg if self.with_xg else None


def shot_summary(shots: pd.DataFrame) -> ShotSummary:
    return ShotSummary(
        count=len(shots),
        goals=int((shots.outcome == "Goal").sum()),
        xg=float(shots.xg.sum(skipna=True)),
        with_xg=int(shots.xg.notna().sum()),
    )


# StatsBomb shot.outcome → marker group on the shot map (CLAUDE.md 5.8)
SHOT_RESULTS = {
    "Goal": "goal",
    "Saved": "saved", "Saved to Post": "saved", "Saved Off Target": "saved",
    "Post": "post",
    "Blocked": "blocked",
    "Off T": "off", "Wayward": "off",
}
SHOT_TYPES = {"Open Play": "openPlay", "Free Kick": "freeKick", "Penalty": "penalty",
              "Corner": "corner", "Kick Off": "kickOff"}
BODY_PARTS = {"Right Foot": "rightFoot", "Left Foot": "leftFoot", "Head": "head"}


def shot_list(shots: pd.DataFrame) -> pd.DataFrame:
    """The shots in chronological order, with ``result``, ``shot_type_code``, ``set_piece`` and ``body_part_code``.

    Every row of ``shots`` stays: missing xG or location is kept as missing.
    """
    out = shots.sort_values(["period", "index"]).copy()
    out["result"] = out.outcome.map(lambda o: SHOT_RESULTS.get(o, "other"))
    out["shot_type_code"] = out.shot_type.map(lambda t: SHOT_TYPES.get(t, "other"))
    out["set_piece"] = out.shot_type != "Open Play"
    out["body_part_code"] = out.body_part.map(lambda b: BODY_PARTS.get(b, "other"))
    return out


GOAL_POSTS = (36.0, 44.0)  # y of the posts, yards
CROSSBAR = 2.67  # height of the bar, yards


def shot_finish(result: str, x: float, y: float, end_x: float | None, end_y: float | None, end_z: float | None) -> dict:
    """Where the ball ended (CLAUDE.md 5.8, "Desfecho"), in metres, from ``shot.end_location``."""
    m = lambda yd: round(yd * YARDS_TO_METERS, 1)
    height = None if end_z is None or pd.isna(end_z) else m(end_z)
    if result in ("goal", "saved"):
        return {"kind": result, "height": height}
    if result == "post":
        return {"kind": "post"}
    if result == "blocked":
        reached = end_x is not None and not pd.isna(end_x)
        return {"kind": "blocked", "blockedAfter": m(((end_x - x) ** 2 + (end_y - y) ** 2) ** 0.5) if reached else None}
    if result == "off":
        if height is None:
            return {"kind": "short"}
        low, high = GOAL_POSTS
        if low <= end_y <= high:
            return {"kind": "over", "height": height, "wideBy": None}
        wide_by = m(low - end_y if end_y < low else end_y - high)
        return {"kind": "overWide" if end_z > CROSSBAR else "wide", "height": height, "wideBy": wide_by}
    return {"kind": "other"}


@dataclass(frozen=True)
class Substitution:
    minute: int
    out_id: int
    in_id: int
    reason: str | None


def substitutions(events: list[dict], team_id: int, periods: tuple[int, ...] = (1, 2)) -> list[Substitution]:
    subs = [
        Substitution(
            minute=e["minute"],
            out_id=e["player"]["id"],
            in_id=e["substitution"]["replacement"]["id"],
            reason=(e["substitution"].get("outcome") or {}).get("name"),
        )
        for e in sorted(events, key=lambda e: e["index"])
        if e["type"]["name"] == "Substitution" and e["team"]["id"] == team_id and e["period"] in periods
    ]
    return subs

