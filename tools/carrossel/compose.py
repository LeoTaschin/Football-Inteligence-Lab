"""Compose LinkedIn slides (1080x1350 drawn at 2x) from site captures. Usage: compose.py <raw> <fonts> <post_png> <out>"""

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

RAW, FONTS, POST, OUT = (Path(a) for a in sys.argv[1:5])
OUT.mkdir(parents=True, exist_ok=True)

X = 2  # render scale
W, H, PAD = 1080 * X, 1350 * X, 56 * X
TEXT, TEXT2, MUTED, BORDER, GREEN = "#0A0A0B", "#3F3F46", "#6B6B73", "#E4E4E7", "#009C3B"


def font(weight: str, px: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONTS / f"Inter-{weight}.ttf"), px * X)


def wrap(draw, text, fnt, width):
    lines, line = [], ""
    for word in text.split():
        trial = f"{line} {word}".strip()
        if draw.textlength(trial, font=fnt) <= width or not line:
            line = trial
        else:
            lines.append(line)
            line = word
    return lines + [line]


def paragraph(draw, xy, text, fnt, width, color, line_h):
    x, y = xy
    for ln in wrap(draw, text, fnt, width):
        draw.text((x, y), ln, font=fnt, fill=color)
        y += line_h * X
    return y


def fit(img: Image.Image, max_w: int, max_h: int) -> Image.Image:
    k = min(max_w / img.width, max_h / img.height)
    return img.resize((round(img.width * k), round(img.height * k)), Image.LANCZOS)


def slide(page: int, total: int, title: str, subtitle: str):
    im = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(im)
    d.text((PAD, PAD), "F.I.L · PROJETO 01 · PNSM", font=font("SemiBold", 14), fill=MUTED)
    d.text((W - PAD, PAD), f"{page}/{total}", font=font("SemiBold", 14), fill=MUTED, anchor="ra")
    y = PAD + 34 * X
    y = paragraph(d, (PAD, y), title, font("ExtraBold", 46), W - 2 * PAD, TEXT, 52)
    y += 10 * X
    y = paragraph(d, (PAD, y), subtitle, font("Regular", 21), W - 2 * PAD, TEXT2, 30)
    d.line([(PAD, H - PAD - 34 * X), (W - PAD, H - PAD - 34 * X)], fill=BORDER, width=X)
    d.text((PAD, H - PAD - 18 * X), "Dados: StatsBomb Open Data", font=font("Regular", 14), fill=MUTED)
    d.text((W - PAD, H - PAD - 18 * X), "Leonardo Taschin · F.I.L", font=font("Regular", 14), fill=MUTED, anchor="ra")
    return im, d, y + 32 * X


def place(im, img, top, bottom, border=True):
    img = fit(img, W - 2 * PAD, bottom - top)
    x = (W - img.width) // 2
    y = top + 8 * X  # right under the header
    im.paste(img, (x, y))
    if border:
        ImageDraw.Draw(im).rectangle([x - X, y - X, x + img.width, y + img.height], outline=BORDER, width=X)


def raw(name):
    return Image.open(RAW / name).convert("RGB")


BOTTOM = H - PAD - 60 * X
slides = []
TOTAL = 7

# 1 · cover: the generated post
slides.append(Image.open(POST).convert("RGB").resize((W, H), Image.LANCZOS))

# 2 · every map of the final in one image
im, d, top = slide(2, TOTAL, "Todos os mapas da final, num lugar só",
                   "Brasil 4 × 1 Itália, 21 de junho de 1970. Quatro leituras da mesma partida, todas a partir dos dados de eventos.")
cells = [
    ("net_bra.png", "Rede de passes · Brasil", "400 passes completos; eixo Gérson – Carlos Alberto (44)"),
    ("net_ita.png", "Rede de passes · Itália", "243 passes completos; 2 substituições na rede"),
    ("phases_def.png", "Com bola × sem bola", "o time recua 16,5 m em média sem a bola"),
    ("replay_pitch.png", "Replay do 4º gol", "9 passes, 8 jogadores, 29 s até o chute"),
]
gap = 28 * X
cw = (W - 2 * PAD - gap) // 2
pic_h = cw * 2 // 3  # pitches are 3:2
ch = pic_h + 58 * X
block = 2 * ch + gap
start = top + 8 * X  # grid right under the header
for i, (name, cap, sub) in enumerate(cells):
    cx = PAD + (i % 2) * (cw + gap)
    cy = start + (i // 2) * (ch + gap)
    img = fit(raw(name), cw, pic_h)
    im.paste(img, (cx, cy))
    d.rectangle([cx - X, cy - X, cx + img.width, cy + img.height], outline=BORDER, width=X)
    d.text((cx, cy + img.height + 12 * X), cap, font=font("Bold", 17), fill=TEXT)
    d.text((cx, cy + img.height + 36 * X), sub, font=font("Regular", 14), fill=MUTED)
slides.append(im)
im.save(OUT / "mapas_da_final.png", optimize=True)

# 3 · selecting a player
im, d, top = slide(3, TOTAL, "Clique em um jogador",
                   "As setas mostram para quem ele passou e de quem recebeu. Gérson: 70 passes dados, 77 recebidos, 26 deles para Carlos Alberto.")
place(im, raw("selected.png"), top, BOTTOM, border=False)
slides.append(im)

# 4 · with and without the ball
im, d, top = slide(4, TOTAL, "Com bola × sem bola",
                   "Onde cada jogador agia com a bola e onde fazia ações defensivas. Carlos Alberto muda 34 m; Pelé é o único que defende mais à frente do que ataca.")
place(im, raw("phases_full.png"), top, BOTTOM, border=False)
slides.append(im)

# 5 · goal replay
im, d, top = slide(5, TOTAL, "O 4º gol, passe a passe",
                   "Reconstruído só com os eventos da jogada: da recuperação de Tostão no próprio campo ao chute de Carlos Alberto.")
place(im, raw("replay_full.png"), top, BOTTOM, border=False)
slides.append(im)

# 6 · campaign
im, d, top = slide(6, TOTAL, "A campanha inteira",
                   "Seis jogos, seis vitórias, 2.490 passes completos. Carlos Alberto foi quem mais passou (367) e está nas duas duplas mais usadas.")
place(im, raw("campaign.png"), top, BOTTOM, border=False)
slides.append(im)

# 7 · how it was built
im, d, top = slide(7, TOTAL, "Como foi feito",
                   "Um motor em Python é a única fonte dos números: o mesmo código gera os dados do site e a imagem do post.")
steps = ["load", "transform", "metrics", "validate", "export", "site · post"]
f_step = font("SemiBold", 19)
y = top + 8 * X
x = PAD
for i, s in enumerate(steps):
    w = d.textlength(s, font=f_step) + 28 * X
    if x + w > W - PAD:
        x, y = PAD, y + 62 * X
    end = i == len(steps) - 1
    d.rounded_rectangle([x, y, x + w, y + 46 * X], radius=8 * X, outline=TEXT if end else "#D4D4D8", width=X * (2 if end else 1))
    d.text((x + 14 * X, y + 23 * X), s, font=f_step, fill=TEXT, anchor="lm")
    x += w
    if not end:
        d.text((x + 10 * X, y + 23 * X), "→", font=f_step, fill="#A1A1AA", anchor="lm")
        x += 36 * X
y += 104 * X
facts = [
    ("Regras explícitas e testadas", "passe completo = sem pass.outcome; agregação por ID do jogador, nunca pelo nome; cada passe excluído conta num único motivo."),
    ("Validação antes de publicar", "a soma das conexões é igual aos passes completos (400 = 400 na final); gols batem com o placar. Se algo falha, nada é exportado."),
    ("Conferido contra a referência", "57 testes automáticos, incluindo os números da final e da campanha."),
    ("Integração contínua", "GitHub Actions roda os testes e confere se os dados do site estão em dia a cada mudança; a Vercel publica."),
    ("Stack", "Python (pandas, matplotlib) · React + TypeScript · SVG · Vite · Vercel."),
]
for head, body in facts:
    d.ellipse([PAD, y + 10 * X, PAD + 12 * X, y + 22 * X], fill=GREEN)
    d.text((PAD + 28 * X, y), head, font=font("Bold", 23), fill=TEXT)
    y = paragraph(d, (PAD + 28 * X, y + 36 * X), body, font("Regular", 20), W - 2 * PAD - 28 * X, TEXT2, 30) + 34 * X
d.text((PAD, y + 16 * X), "github.com/LeoTaschin/Football-Inteligence-Lab", font=font("Bold", 21), fill=TEXT)
slides.append(im)

for i, s in enumerate(slides, start=1):
    s.save(OUT / f"slide_{i}.png", optimize=True)
slides[0].save(OUT / "carrossel_PNSM.pdf", save_all=True, append_images=slides[1:], resolution=144)
print("ok", sorted(p.name for p in OUT.iterdir()))
