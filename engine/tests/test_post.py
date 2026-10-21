from pathlib import Path

import pytest

pytest.importorskip("matplotlib")

from matplotlib.image import imread  # noqa: E402

from conftest import FINAL  # noqa: E402
from pnsm import export, load  # noqa: E402
from pnsm.config import CollectionConfig  # noqa: E402
from pnsm.report.post import _finding, _subs_line, render_post  # noqa: E402

CONFIG = Path(__file__).parents[1] / "config" / "wc1970_brazil.yaml"


@pytest.fixture(scope="module")
def final_data():
    cfg = CollectionConfig.from_yaml(CONFIG)
    meta = load.find_match(FINAL, cfg.competition_id, cfg.season_id)
    return export.build_match(meta, load.load_events(FINAL), load.load_lineups(FINAL), cfg)


@pytest.mark.regression
def test_post_texts_come_from_the_data(final_data):
    brazil, italy = final_data["teams"]
    text = "".join(r.text for r in _finding(brazil, italy))
    assert text == ("O Brasil completou 400 passes, 157 a mais que a Itália, e fez o jogo girar pelo eixo "
                    "Gérson – Carlos Alberto: 44 passes entre os dois.")
    assert _subs_line(final_data["teams"]) == "A Itália fez duas substituições (74′ e 83′); o Brasil jogou com os mesmos 11."


@pytest.mark.regression
def test_post_is_1080_by_1350(final_data, tmp_path):
    out = render_post(final_data, tmp_path / "post.png")
    assert imread(out).shape[:2] == (1350, 1080)


def test_subs_line_capitalizes_only_the_sentence_start():
    teams = [
        {"article": "o", "displayName": "Brasil", "substitutions": [{"minute": 66}, {"minute": 79}]},
        {"article": "o", "displayName": "Peru", "substitutions": [{"minute": 52}, {"minute": 59}]},
    ]
    assert _subs_line(teams) == "O Brasil fez duas substituições (66′ e 79′); o Peru fez duas substituições (52′ e 59′)."
