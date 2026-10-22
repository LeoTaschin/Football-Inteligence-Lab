"""Instagram carousel (7 slides, 1080x1350, drawn at 2x) on the campaign's xG: 19 goals from 14.75 expected.

Usage: instagram_xg.py <site_data_dir> <raw_captures> <fonts> <out>
Every number comes from the engine's exported JSON (site/public/data); the shot map of the
final is a capture of the site (capture_etapa2.py writes shots_goal.png).
"""

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

import layout
from layout import BORDER, H, MUTED, PAD, TEXT, TEXT2, W, X, fit, font, paragraph, slide

DATA, RAW, FONTS, OUT = (Path(a) for a in sys.argv[1:5])
layout.FONTS = FONTS
OUT.mkdir(parents=True, exist_ok=True)

KICKER = "F.I.L · FOOTBALL INTELLIGENCE LAB"
SITE = "football-inteligence-lab-nine.vercel.app"
UNLIKELY, CLEAR = "#009C3B", "#8A8A93"  # validated pair (dataviz validate_palette: CVD ΔE 10.2, contrast ≥ 3:1)
LINE, SURFACE = "#D4D4D8", "#F7F7F8"
LOW = 0.10  # "improvável": less than 10% chance
BOTTOM = H - PAD - 60 * X
TOTAL = 7


def dec(v, d=2):
    return f"{v:.{d}f}".replace(".", ",")


def pct(xg):
    return f"{dec(100 * xg, 1)}%" if xg < 0.1 else f"{round(100 * xg)}%"


# --- data -----------------------------------------------------------------------------
collection = json.loads((DATA / "collections" / "wc1970-brazil.json").read_text(encoding="utf-8"))
s = collection["summary"]
goals, shots = [], 0
for m in collection["matches"]:
    match = json.loads((DATA / "matches" / f"{m['id']}.json").read_text(encoding="utf-8"))
    team = match["teams"][0]
    shots += team["shots"]["count"]
    for sh in team["shots"]["items"]:
        if sh["result"] == "goal":
            goals.append({**sh, "opponent": m["opponent"], "order": m["order"]})
assert len(goals) == s["goalsFor"], "every goal of the campaign is a shot (no own goals)"
low = [g for g in goals if g["xg"] < LOW]
jair = [g for g in goals if g["name"] == "Jairzinho"]
games_jair = len({g["order"] for g in jair})


def text_block(d, top, items, bottom=BOTTOM):
    """Paragraphs [(text, font, color, line_height, space_after)] centred between top and bottom."""
    height = sum(len(layout.wrap(d, t, f, W - 2 * PAD)) * lh * X + after * X for t, f, _, lh, after in items)
    y = top + max(0, (bottom - top - height) / 2)
    for t, f, color, lh, after in items:
        y = paragraph(d, (PAD, y), t, f, W - 2 * PAD, color, lh) + after * X
    return y


slides = []

# 1 · cover
im, d, top = slide(1, TOTAL, "Pela estatística, o Brasil de 1970 deveria ter feito 15 gols.",
                   "Fez 19. Fui atrás de onde vieram os outros 4.", kicker=KICKER)
y = top + 40 * X
for value, label in ((dec(s["xgFor"]), f"gols esperados (xG) em {shots} chutes"), (str(s["goalsFor"]), "gols feitos")):
    d.text((PAD, y), value, font=font("ExtraBold", 150), fill=TEXT)
    d.text((PAD + 6 * X, y + 178 * X), label, font=font("SemiBold", 26), fill=TEXT2)
    y += 260 * X
paragraph(d, (PAD, y + 10 * X), f"+{dec(s['goalsFor'] - s['xgFor'])} gols acima do esperado. Sorte? Vamos olhar gol a gol.", font("Bold", 30), W - 2 * PAD, TEXT, 40)
d.text((PAD, BOTTOM - 40 * X), "Campanha do tri · 6 jogos · dados de eventos StatsBomb", font=font("Regular", 20), fill=MUTED)
slides.append(im)

# 2 · what xG is
im, d, top = slide(2, TOTAL, "O que é xG?",
                   "Gols esperados: para cada chute, a chance de ele virar gol, estimada a partir de milhares de chutes parecidos: distância, ângulo, parte do corpo, tipo de jogada.",
                   kicker=KICKER)
y = top + 30 * X
examples = [
    (max(jair, key=lambda g: g["xg"]), "chance clara"),
    (min(goals, key=lambda g: abs(g["xg"] - 0.30)), "uma chance em quatro"),
    (next(g for g in goals if g["name"] == "Carlos Alberto"), "quase impossível"),
]
for g, tag in examples:
    d.rounded_rectangle([PAD, y, W - PAD, y + 150 * X], radius=14 * X, outline=BORDER, width=X)
    d.text((PAD + 28 * X, y + 30 * X), pct(g["xg"]), font=font("ExtraBold", 60), fill=UNLIKELY if g["xg"] < LOW else TEXT)
    d.text((PAD + 300 * X, y + 38 * X), f"{g['name']} × {g['opponent']}", font=font("Bold", 26), fill=TEXT)
    d.text((PAD + 300 * X, y + 80 * X), f"{tag} · {round(g['distance'])} m do gol", font=font("Regular", 22), fill=TEXT2)
    y += 178 * X
paragraph(d, (PAD, y + 10 * X), "Somando o xG de todos os chutes, sai quantos gols um time “deveria” ter feito.", font("Regular", 24), W - 2 * PAD, TEXT2, 34)
slides.append(im)

# 3 · the 19 goals by xG (horizontal bars, threshold at 10%)
im, d, top = slide(3, TOTAL, f"{len(low)} dos {len(goals)} gols vieram de chances com menos de 10%",
                   "Cada barra é um gol, do menos provável ao mais provável.", kicker=KICKER)
rows = sorted(goals, key=lambda g: g["xg"])
label_w, value_w = 360 * X, 90 * X
x0, x1 = PAD + label_w, W - PAD - value_w
y = top + 30 * X
row_h = (BOTTOM - y - 70 * X) / len(rows)
bar_h = row_h - 8 * X
scale = lambda v: x0 + (x1 - x0) * v
for g in rows:
    color = UNLIKELY if g["xg"] < LOW else CLEAR
    d.text((PAD, y + bar_h / 2), f"{g['name']} × {g['opponent']} {g['minute']}′", font=font("SemiBold" if g["xg"] < LOW else "Regular", 19), fill=TEXT, anchor="lm")
    d.rounded_rectangle([x0, y, max(x0 + 8 * X, scale(g["xg"])), y + bar_h], radius=4 * X, fill=color)
    # values of the short bars start after the 10% line so it never crosses them
    d.text((max(x0 + 8 * X, scale(g["xg"]), scale(LOW) + 4 * X) + 10 * X, y + bar_h / 2), pct(g["xg"]), font=font("Bold", 19), fill=TEXT, anchor="lm")
    y += row_h
# 10% reference line
lx = scale(LOW)
d.line([(lx, top + 20 * X), (lx, y)], fill=TEXT, width=2 * X)
d.text((lx + 8 * X, top + 6 * X), "10%", font=font("Bold", 18), fill=TEXT)
ly = y + 22 * X
for color, text in ((UNLIKELY, "improvável: menos de 10% de chance"), (CLEAR, "chance mais clara")):
    d.rounded_rectangle([PAD, ly, PAD + 22 * X, ly + 22 * X], radius=4 * X, fill=color)
    d.text((PAD + 34 * X, ly + 11 * X), text, font=font("Regular", 20), fill=TEXT2, anchor="lm")
    ly += 34 * X
slides.append(im)

# 4 · where the 19 goals came from (vertical half pitch)
im, d, top = slide(4, TOTAL, "Dois tipos de gol",
                   f"Jairzinho fez {len(jair)}, um em cada jogo, quase todos de perto. Os improváveis saíram de longe: Rivellino, Pelé, Gérson, Carlos Alberto.",
                   kicker=KICKER)
Y0, Y1 = 8, 72  # sides cropped: every goal is between these touchline distances
pw = W - 2 * PAD
k = pw / (Y1 - Y0)  # px per yard
# deep enough for the farthest goal, in 5-yard steps
depth = int(((120 - min(g["x"] for g in goals)) // 5 + 2) * 5)
ph = depth * k
px0, py0 = PAD, top + 20 * X


def pt(x, y):
    return px0 + (y - Y0) * k, py0 + (120 - x) * k


d.rectangle([px0, py0, px0 + pw, py0 + ph], fill=SURFACE, outline=LINE, width=X)
d.rectangle([*pt(120, 18), *pt(102, 62)], outline=LINE, width=X)
d.arc([*pt(108 + 10, 30), *pt(108 - 10, 50)], start=37, end=143, fill=LINE, width=X)
d.rectangle([*pt(120, 30), *pt(114, 50)], outline=LINE, width=X)
gx0, gy0 = pt(120, 36)
gx1, _ = pt(120, 44)
d.rectangle([gx0, gy0 - 5 * X, gx1, gy0], fill=TEXT)
for g in sorted(goals, key=lambda g: g["xg"] < LOW):
    cx, cy = pt(g["x"], g["y"])
    r = 13 * X
    is_low = g["xg"] < LOW
    d.ellipse([cx - r - 3 * X, cy - r - 3 * X, cx + r + 3 * X, cy + r + 3 * X], fill="white")  # surface ring
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=UNLIKELY if is_low else CLEAR)
    if g["name"] == "Jairzinho":
        d.text((cx, cy), "J", font=font("ExtraBold", 13), fill="white", anchor="mm")
ly = py0 + ph + 26 * X
for color, text in ((UNLIKELY, "improvável (menos de 10%)"), (CLEAR, "chance mais clara · J = Jairzinho")):
    d.ellipse([PAD, ly, PAD + 22 * X, ly + 22 * X], fill=color)
    d.text((PAD + 34 * X, ly + 11 * X), text, font=font("Regular", 20), fill=TEXT2, anchor="lm")
    ly += 34 * X
far = [g for g in low if g["distance"] >= 15]
mean = lambda xs: sum(xs) / len(xs)
y = ly + 30 * X
cw = (W - 2 * PAD - 24 * X) // 2
for i, (title, group, color) in enumerate((("Gols de Jairzinho", jair, CLEAR), (f"Os {len(low)} improváveis", low, UNLIKELY))):
    cx = PAD + i * (cw + 24 * X)
    d.rounded_rectangle([cx, y, cx + cw, y + 190 * X], radius=14 * X, outline=BORDER, width=X)
    d.ellipse([cx + 24 * X, y + 28 * X, cx + 44 * X, y + 48 * X], fill=color)
    d.text((cx + 56 * X, y + 38 * X), title, font=font("Bold", 22), fill=TEXT, anchor="lm")
    d.text((cx + 24 * X, y + 70 * X), pct(mean([g["xg"] for g in group])), font=font("ExtraBold", 52), fill=TEXT)
    d.text((cx + 24 * X, y + 136 * X), f"xG médio · {round(mean([g['distance'] for g in group]))} m do gol em média", font=font("Regular", 19), fill=TEXT2)
paragraph(d, (PAD, y + 220 * X), f"{len(far)} dos {len(low)} gols improváveis foram chutados a 15 m ou mais do gol.", font("Bold", 24), W - 2 * PAD, TEXT, 34)
slides.append(im)

# 5 · the final
fin = [g for g in goals if g["order"] == 6]
im, d, top = slide(5, TOTAL, "Na final, 3 dos 4 gols eram improváveis",
                   " · ".join(f"{g['name']} {pct(g['xg'])}" for g in sorted(fin, key=lambda g: g["minute"])) + ". E a maior chance do jogo, de Pelé (79%), foi para fora.",
                   kicker=KICKER)
img = fit(Image.open(RAW / "shots_goal.png").convert("RGB"), W - 2 * PAD, BOTTOM - top - 8 * X)
im.paste(img, ((W - img.width) // 2, top + 8 * X))
slides.append(im)

# 6 · what the model cannot see
im, d, top = slide(6, TOTAL, "O xG não sabe quem está chutando",
                   "Ele mede a chance de um chute médio naquela situação. Aquele time tinha Rivellino, Gérson e Pelé batendo de longe.",
                   kicker=KICKER)
text_block(d, top, [
    ("Os 4 gols “a mais” talvez não sejam sorte. Talvez sejam exatamente o que o modelo não consegue ver.", font("Bold", 42), TEXT, 56, 56),
    ("Ressalva: os dados de 1970 foram registrados a partir de vídeos da época. Localização e xG têm mais incerteza que num jogo de hoje.", font("Regular", 26), TEXT2, 38, 56),
    ("Próximo passo do F.I.L: construir o meu próprio modelo de xG.", font("Bold", 32), TEXT, 44, 0),
])
slides.append(im)

# 7 · call to action
im, d, top = slide(7, TOTAL, "Explore todos os chutes", "Cada chute da campanha, o caminho da bola e uma página para cada um dos 93 jogadores.", kicker=KICKER)
text_block(d, top, [
    ("Link na bio", font("ExtraBold", 72), TEXT, 84, 8),
    (SITE, font("SemiBold", 28), TEXT2, 40, 90),
    ("E pra você: um modelo de xG deveria levar em conta quem está chutando?", font("Bold", 42), TEXT, 56, 20),
    ("Responde nos comentários.", font("Regular", 28), TEXT2, 40, 0),
])
slides.append(im)

for i, im in enumerate(slides, start=1):
    im.resize((1080, 1350), Image.LANCZOS).save(OUT / f"instagram_xg_{i}.png", optimize=True)
print("ok", len(slides), "slides;", f"{len(low)} improváveis, Jairzinho {len(jair)} gols em {games_jair} jogos")
