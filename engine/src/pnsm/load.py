"""Download and cache StatsBomb Open Data JSON files.

Files are stored under ``engine/.cache/`` with the same relative path as in the
open-data repository (``events/3888702.json``...). Once cached, a file is never
downloaded again: the open data is static.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

import requests

BASE_URL = "https://raw.githubusercontent.com/statsbomb/open-data/master/data"
DEFAULT_CACHE_DIR = Path(__file__).resolve().parents[2] / ".cache"
TIMEOUT_SECONDS = 60


def fetch_json(
    rel_path: str,
    cache_dir: Path = DEFAULT_CACHE_DIR,
    session: requests.Session | None = None,
) -> Any:
    """Return the parsed JSON at ``rel_path``, downloading it only if not cached."""
    path = Path(cache_dir) / rel_path
    if not path.exists():
        http = session or requests
        response = http.get(f"{BASE_URL}/{rel_path}", timeout=TIMEOUT_SECONDS)
        response.raise_for_status()
        _write_atomic(path, response.content)
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _write_atomic(path: Path, content: bytes) -> None:
    # write to a temp file and rename, so an interrupted download never leaves a broken cache entry
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".part")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(content)
        os.replace(tmp, path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


def load_competitions(cache_dir: Path = DEFAULT_CACHE_DIR) -> list[dict]:
    return fetch_json("competitions.json", cache_dir)


def load_matches(competition_id: int, season_id: int, cache_dir: Path = DEFAULT_CACHE_DIR) -> list[dict]:
    return fetch_json(f"matches/{competition_id}/{season_id}.json", cache_dir)


def load_events(match_id: int, cache_dir: Path = DEFAULT_CACHE_DIR) -> list[dict]:
    return fetch_json(f"events/{match_id}.json", cache_dir)


def load_lineups(match_id: int, cache_dir: Path = DEFAULT_CACHE_DIR) -> list[dict]:
    return fetch_json(f"lineups/{match_id}.json", cache_dir)


def find_match(match_id: int, competition_id: int, season_id: int, cache_dir: Path = DEFAULT_CACHE_DIR) -> dict:
    """Match metadata (teams, score, date, stage, stadium) from the season file."""
    for match in load_matches(competition_id, season_id, cache_dir):
        if match["match_id"] == match_id:
            return match
    raise KeyError(f"match {match_id} not found in competition {competition_id}, season {season_id}")


def fetch_season(
    competition_id: int,
    season_id: int,
    team: str | None = None,
    cache_dir: Path = DEFAULT_CACHE_DIR,
) -> list[int]:
    """Cache events and lineups of every match in a season (optionally only one team's).

    Returns the match ids in chronological order.
    """
    matches = load_matches(competition_id, season_id, cache_dir)
    if team is not None:
        matches = [m for m in matches if team in (m["home_team"]["home_team_name"], m["away_team"]["away_team_name"])]
    matches = sorted(matches, key=lambda m: (m["match_date"], m.get("kick_off") or ""))
    for match in matches:
        load_events(match["match_id"], cache_dir)
        load_lineups(match["match_id"], cache_dir)
    return [m["match_id"] for m in matches]
