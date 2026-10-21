"""Display names (pt-BR) for players, positions and teams.

Labels are only text: every aggregation uses ``player_id``.
"""

from __future__ import annotations

from dataclasses import dataclass

# StatsBomb player_name -> display name, for cases the automatic rule gets wrong
NAME_OVERRIDES = {
    "Édson Arantes do Nascimento": "Pelé",
    "Roberto Rivelino": "Rivellino",
    "Eduardo Gonçalves de Andrade": "Tostão",  # StatsBomb nickname is "Tostao"
    "Wilson da Silva Piazza": "Piazza",  # StatsBomb nickname is "Wilson Piazza"
    "Giancarlo De Sisti": "De Sisti",
}

PARTICLES = {"de", "da", "do", "dos", "das", "del", "della", "di", "van", "von", "der", "den", "ter", "le", "la"}

POSITIONS = {
    "Goalkeeper": "Goleiro",
    "Right Back": "Lateral-direito",
    "Left Back": "Lateral-esquerdo",
    "Right Wing Back": "Ala-direito",
    "Left Wing Back": "Ala-esquerdo",
    "Center Back": "Zagueiro",
    "Right Center Back": "Zagueiro (dir.)",
    "Left Center Back": "Zagueiro (esq.)",
    "Center Defensive Midfield": "Volante",
    "Right Defensive Midfield": "Volante (dir.)",
    "Left Defensive Midfield": "Volante (esq.)",
    "Center Midfield": "Meia",
    "Right Center Midfield": "Meia (dir.)",
    "Left Center Midfield": "Meia (esq.)",
    "Right Midfield": "Meio-campo (dir.)",
    "Left Midfield": "Meio-campo (esq.)",
    "Center Attacking Midfield": "Meia-atacante",
    "Right Attacking Midfield": "Meia-atacante (dir.)",
    "Left Attacking Midfield": "Meia-atacante (esq.)",
    "Right Wing": "Ponta-direita",
    "Left Wing": "Ponta-esquerda",
    "Center Forward": "Centroavante",
    "Right Center Forward": "Atacante (dir.)",
    "Left Center Forward": "Atacante (esq.)",
    "Secondary Striker": "Segundo atacante",
}

TEAMS = {
    "Brazil": "Brasil",
    "Italy": "Itália",
    "Czechoslovakia": "Tchecoslováquia",
    "England": "Inglaterra",
    "Romania": "Romênia",
    "Peru": "Peru",
    "Uruguay": "Uruguai",
}

STAGES = {
    "Group Stage": "Fase de grupos",
    "Quarter-finals": "Quartas de final",
    "Semi-finals": "Semifinal",
    "Final": "Final",
}


def surname(full_name: str) -> str:
    """Last word plus any particles before it: "Kevin De Bruyne" -> "De Bruyne"."""
    words = full_name.split()
    label = [words.pop()]
    while words and words[-1].lower() in PARTICLES:
        label.insert(0, words.pop())
    return " ".join(label)


def display_name(player_name: str, nickname: str | None) -> str:
    if player_name in NAME_OVERRIDES:
        return NAME_OVERRIDES[player_name]
    if nickname and nickname.strip():
        return nickname.strip()
    return surname(player_name)


def position_pt(position: str | None) -> str | None:
    if position is None:
        return None
    return POSITIONS.get(position, position)


def team_pt(team: str) -> str:
    return TEAMS.get(team, team)


def stage_pt(stage: str) -> str:
    return STAGES.get(stage, stage)


@dataclass(frozen=True)
class Player:
    player_id: int
    num: int | None
    name: str
    position: str | None  # pt-BR, from the first position played


def players_from_lineup(team_lineup: dict) -> dict[int, Player]:
    """``{player_id: Player}`` for one team entry of the lineups file.

    Two players of the same team with the same display name get the shirt number appended.
    """
    players = {}
    for p in team_lineup["lineup"]:
        positions = p.get("positions") or []
        players[p["player_id"]] = Player(
            player_id=p["player_id"],
            num=p.get("jersey_number"),
            name=display_name(p["player_name"], p.get("player_nickname")),
            position=position_pt(positions[0]["position"]) if positions else None,
        )
    seen: dict[str, int] = {}
    for player in players.values():
        seen[player.name] = seen.get(player.name, 0) + 1
    return {
        pid: Player(p.player_id, p.num, f"{p.name} {p.num}", p.position) if seen[p.name] > 1 else p
        for pid, p in players.items()
    }
