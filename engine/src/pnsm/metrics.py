"""Pass network, shot and phase metrics (CLAUDE.md, section 5).

Every function receives tables already filtered by ``transform`` and aggregates by
``player_id``. Nothing here filters events again.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


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

