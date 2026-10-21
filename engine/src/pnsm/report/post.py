"""LinkedIn post, 1080 × 1350 (CLAUDE.md 7.6), drawn from the same data as the site."""

from __future__ import annotations

from pathlib import Path

from pnsm.report import theme
from pnsm.report.components import Canvas, Run, draw_network

W, H = 1080, 1350
PAD = 56
GAP = 32
PITCH_W = (W - 2 * PAD - GAP) // 2  # 468
PITCH_H = PITCH_W * 2 // 3  # 312
TOP = 10

MONTHS = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
COMPETITIONS = {"FIFA World Cup": "Copa do Mundo"}
COUNT = {2: "duas", 3: "três", 4: "quatro"}


def render_post(data: dict, out: Path, min_pair: int = 3) -> Path:
    """Draw the post for one exported match (``export.build_match`` output) and save it as PNG."""
    family = theme.ensure_inter()
    c = Canvas(W, H, family)
    match, teams, scale = data["match"], data["teams"], data["scale"]
    home, away = teams

    # --- header -------------------------------------------------------------------
    y = PAD
    c.text(PAD, y, _context(match).upper(), 14, theme.TEXT_MUTED, 600)
    c.text(W - PAD, y, "F.I.L", 14, theme.TEXT, 800, ha="right")
    y += 31
    c.runs(PAD, y, [
        Run(f"{home['displayName']} ", theme.TEXT, 800),
        Run(str(match["score"][0]), home["colors"]["line"], 800),
        Run(" × ", theme.TEXT_FAINT, 500),
        Run(str(match["score"][1]), away["colors"]["line"], 800),
        Run(f" {away['displayName']}", theme.TEXT, 800),
    ], 64)
    y += 78
    y = c.paragraph(PAD, y, _finding(home, away), 22, 900, 31)

    # --- networks -----------------------------------------------------------------
    y += GAP
    for i, team in enumerate(teams):
        x = PAD + i * (PITCH_W + GAP)
        c.dot(x + 6, y + 14, 5, team["colors"]["fill"], team["colors"]["line"])
        c.text(x + 22, y + 2, team["displayName"], 22, theme.TEXT, 700)
        passes = team["passes"]
        c.text(x + PITCH_W, y + 8, f"{passes['completed']} passes completos · "
               f"{round(100 * passes['completed'] / passes['attempted'])}% de acerto", 14, theme.TEXT_MUTED, ha="right")
        ax = c.pitch(x, y + 39, PITCH_W, PITCH_H)
        draw_network(ax, team, PITCH_W, scale["maxPasses"], scale["maxPair"], min_pair, family)
    y += 39 + PITCH_H

    # --- legend -------------------------------------------------------------------
    y += 22
    size_label = "Tamanho = passes completos do jogador"
    width_label = f"Espessura = passes trocados pela dupla (mín. {min_pair})"
    total = 18 + 8 + 10 + 8 + c.measure(size_label, 14) + 32 + 28 + 8 + c.measure(width_label, 14)
    x = (W - total) / 2
    c.dot(x + 9, y + 9, 9, theme.TEXT_FAINT)
    c.dot(x + 18 + 8 + 5, y + 9, 5, theme.TEXT_FAINT)
    x += 18 + 8 + 10 + 8
    c.text(x, y + 1, size_label, 14, theme.TEXT_MUTED)
    x += c.measure(size_label, 14) + 32
    c.rect(x, y + 7, 28, 5, theme.TEXT_FAINT, radius=2.5)
    c.text(x + 36, y + 1, width_label, 14, theme.TEXT_MUTED)

    # --- top 10 combinations ------------------------------------------------------
    y += 18 + GAP
    for i, team in enumerate(teams):
        _top_table(c, team, PAD + i * (PITCH_W + GAP), y, scale["maxPair"])

    # --- footer -------------------------------------------------------------------
    footer = (f"Passes completos com destinatário, {_periods(data['periods'])}. Posição = mediana dos passes do "
              f"jogador. {_subs_line(teams)}")
    footer_y = H - PAD - 2 * 19.5
    c.paragraph(PAD, footer_y, [Run(footer, theme.TEXT_MUTED)], 13, 680, 19.5)
    c.text(W - PAD, footer_y, "Dados: StatsBomb Open Data", 13, theme.TEXT_MUTED, ha="right")
    c.text(W - PAD, footer_y + 19.5, "Leonardo Taschin · F.I.L", 13, theme.TEXT_MUTED, ha="right")

    out.parent.mkdir(parents=True, exist_ok=True)
    c.save(out)
    return out


def _top_table(c: Canvas, team: dict, x: float, y: float, max_pair: int) -> None:
    name = {n["playerId"]: n["name"] for n in team["nodes"]}
    c.text(x, y, f"Top {TOP} combinações · {team['displayName']}", 18, theme.TEXT, 700)
    c.text(x + PITCH_W, y + 5, "→ ida · ← volta", 12, theme.TEXT_MUTED, ha="right")
    y += 30
    c.hline(x, y, PITCH_W)
    y += 6
    bar_x, bar_w = x + PITCH_W - 150, 116
    for rank, p in enumerate(team["pairs"][:TOP], start=1):
        c.text(x, y + 9, str(rank), 13, theme.TEXT_MUTED)
        c.text(x + 32, y + 1, f"{name[p['a']]} – {name[p['b']]}", 14, theme.TEXT, 600)
        c.text(x + 32, y + 18, f"→ {p['forward']}  ·  ← {p['backward']}", 11, theme.TEXT_MUTED)
        c.rect(bar_x, y + 11, bar_w, 8, theme.ROW, radius=4)
        c.rect(bar_x, y + 11, max(8, bar_w * p["n"] / max_pair), 8, team["colors"]["line"], radius=4)
        c.text(x + PITCH_W, y + 7, str(p["n"]), 15, theme.TEXT, 700, ha="right")
        y += 31
        c.hline(x, y, PITCH_W, theme.ROW)
        y += 6


def _context(match: dict) -> str:
    year, month, day = (int(v) for v in match["date"].split("-"))
    competition = COMPETITIONS.get(match["competition"], match["competition"])
    stage = f"Final da {competition}" if match["stage"] == "Final" else f"{match['stage']} · {competition}"
    return " · ".join(filter(None, [stage, f"{day} {MONTHS[month - 1]} {year}", match.get("stadium")]))


def _finding(home: dict, away: dict) -> list[Run]:
    diff = home["passes"]["completed"] - away["passes"]["completed"]
    top = home["pairs"][0]
    name = {n["playerId"]: n["name"] for n in home["nodes"]}
    lead = (f"{home['article'].upper()} {home['displayName']} completou {home['passes']['completed']} passes, "
            f"{abs(diff)} a {'mais' if diff >= 0 else 'menos'} que {away['article']} {away['displayName']}, "
            f"e fez o jogo girar pelo eixo")
    return [
        Run(lead + " ", theme.TEXT_2),
        Run(f"{name[top['a']]} – {name[top['b']]}", theme.TEXT, 700),
        Run(f": {top['n']} passes entre os dois.", theme.TEXT_2),
    ]


def _periods(periods: list[int]) -> str:
    return "1º e 2º tempos" if periods == [1, 2] else ", ".join(f"período {p}" for p in periods)


def _subs_line(teams: list[dict]) -> str:
    parts, same = [], []
    for t in teams:
        minutes = [s["minute"] for s in t["substitutions"]]
        who = f"{t['article']} {t['displayName']}"
        if minutes:
            n = COUNT.get(len(minutes), str(len(minutes))) if len(minutes) > 1 else "uma"
            noun = "substituições" if len(minutes) > 1 else "substituição"
            parts.append(f"{who} fez {n} {noun} ({' e '.join(f'{m}′' for m in minutes)})")
        else:
            same.append(f"{who} jogou com os mesmos 11")
    if not parts:
        return "Nenhuma das equipes fez substituições."
    sentence = "; ".join(parts + same) + "."
    return sentence[0].upper() + sentence[1:]  # only the start of the sentence is capitalized
