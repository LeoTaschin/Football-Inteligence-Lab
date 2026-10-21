"""Collection config (``engine/config/*.yaml``)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class CollectionConfig:
    collection: str
    competition_id: int
    season_id: int
    team: str
    periods: tuple[int, ...]
    min_pair_passes: int
    defensive_actions: tuple[str, ...]
    output_dir: Path

    @classmethod
    def from_yaml(cls, path: str | Path) -> CollectionConfig:
        path = Path(path)
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        return cls(
            collection=raw["collection"],
            competition_id=int(raw["competition_id"]),
            season_id=int(raw["season_id"]),
            team=raw["team"],
            periods=tuple(int(p) for p in raw["periods"]),
            min_pair_passes=int(raw["min_pair_passes"]),
            defensive_actions=tuple(raw["defensive_actions"]),
            # relative to the config file, so the CLI works from any directory
            output_dir=(path.parent / raw["output_dir"]).resolve(),
        )
