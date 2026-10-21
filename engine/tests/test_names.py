import pytest

from conftest import FINAL
from pnsm import load
from pnsm.names import display_name, players_from_lineup, position_pt, surname


def test_surname_keeps_particles():
    assert surname("Kevin De Bruyne") == "De Bruyne"
    assert surname("Sandro Mazzola") == "Mazzola"


def test_nickname_is_trimmed():
    assert display_name("Everaldo Marques da Silva", "Everaldo ") == "Everaldo"


def test_override_wins_over_nickname():
    assert display_name("Eduardo Gonçalves de Andrade", "Tostao") == "Tostão"
    assert display_name("Wilson da Silva Piazza", "Wilson Piazza") == "Piazza"


def test_unknown_position_is_kept():
    assert position_pt("Right Back") == "Lateral-direito"
    assert position_pt("Sweeper") == "Sweeper"


def test_same_display_name_gets_shirt_number():
    lineup = {"lineup": [
        {"player_id": 1, "player_name": "Eden Hazard", "player_nickname": None, "jersey_number": 10, "positions": []},
        {"player_id": 2, "player_name": "Thorgan Hazard", "player_nickname": None, "jersey_number": 16, "positions": []},
    ]}
    players = players_from_lineup(lineup)
    assert (players[1].name, players[2].name) == ("Hazard 10", "Hazard 16")


@pytest.mark.regression
def test_final_display_names():
    brazil, italy = load.load_lineups(FINAL)
    names = {p.name for p in players_from_lineup(brazil).values()}
    assert {"Pelé", "Rivellino", "Tostão", "Piazza", "Carlos Alberto", "Gérson", "Everaldo"} <= names
    names = {p.name for p in players_from_lineup(italy).values()}
    assert {"De Sisti", "Mazzola", "Albertosi", "Boninsegna", "Rivera", "Juliano"} <= names
