"""Compose the Etapa 2 LinkedIn carousel (1080x1350 drawn at 2x). Usage: compose_etapa2.py <raw> <fonts> <out>"""

import sys
from pathlib import Path

from PIL import Image, ImageDraw

import layout
from layout import BORDER, GREEN, H, MUTED, PAD, TEXT, TEXT2, W, X, fit, font, paragraph, place, slide

RAW, FONTS, OUT = (Path(a) for a in sys.argv[1:4])
layout.FONTS = FONTS
OUT.mkdir(parents=True, exist_ok=True)

KICKER = "F.I.L · PROJETO 01 · PNSM · ETAPA 2"
SITE = "football-inteligence-lab-nine.vercel.app"
BOTTOM = H - PAD - 60 * X
TOTAL = 6


def raw(name):
    return Image.open(RAW / name).convert("RGB")


def page(n, title, subtitle, image):
    im, d, top = slide(n, TOTAL, title, subtitle, kicker=KICKER)
    place(im, raw(image), top, BOTTOM, border=False)
    return im


slides = []

# 1 · cover: the shot map and the open-play network side by side
im, d, top = slide(1, TOTAL, "O Brasil de 1970, mais fundo",
                   "Chutes, recortes da rede de passes e uma página por jogador: a Etapa 2 do PNSM, com dados de eventos de uma Copa de 56 anos atrás.",
                   kicker=KICKER)
# the network across the full width, the shot map under it
gap = 22 * X
caption_h = 30 * X
net = fit(raw("open_play_pitch.png"), W - 2 * PAD, (BOTTOM - top) * 3 // 5)
shots = fit(raw("shots_pitch.png"), W - 2 * PAD, BOTTOM - top - 8 * X - net.height - 2 * caption_h - gap)
y = top + 8 * X
for img, cap in ((net, "Rede do Brasil só com jogo aberto, Rivellino selecionado"), (shots, "Finalizações do Brasil na final")):
    x = (W - img.width) // 2
    im.paste(img, (x, y))
    d.rectangle([x - X, y - X, x + img.width, y + img.height], outline=BORDER, width=X)
    d.text((x, y + img.height + 8 * X), cap, font=font("Regular", 15), fill=MUTED)
    y += img.height + caption_h + gap
slides.append(im)

slides.append(page(2, "3 dos 4 gols do Brasil vieram de chances com xG abaixo de 0,07",
                   "Na final, a maior chance do jogo foi de Pelé aos 46′ (xG 0,79), e foi para fora. Cada ícone é um chute; o halo mostra o xG e o tracejado, o caminho da bola.",
                   "shots.png"))
slides.append(page(3, "Sem bola parada, Rivellino recua 11 m",
                   "Tirando faltas, laterais, escanteios, tiros de meta e saídas de bola, saem 43 passes do Brasil. Faltas e escanteios puxavam a posição de Rivellino para frente; na Itália, Albertosi cai de 32 para 12 passes.",
                   "open_play.png"))
slides.append(page(4, "A Itália só com quem esteve junto em campo",
                   "A rede da partida inteira junta titulares e substitutos. Cortando na 1ª substituição (Bertini, 74′), ficam 193 dos 243 passes, só entre os 11 que jogaram juntos.",
                   "italy_first_sub.png"))
slides.append(page(5, "Uma página por jogador",
                   "93 jogadores, do Brasil e dos adversários. Carlos Alberto: 367 passes, quem mais passou em 3 dos 6 jogos, e recua 26 m em média entre atacar e defender.",
                   "player.png"))

# 6 · call to action
im, d, top = slide(6, TOTAL, "Explore no site",
                   "Tudo interativo: escolha a equipe, o recorte, o chute ou o jogador. Os números vêm de um motor em Python, testado e validado antes de publicar.",
                   kicker=KICKER)
y = top + 24 * X
d.text((PAD, y), SITE, font=font("ExtraBold", 34), fill=TEXT)
y += 92 * X
news = [
    ("Finalizações", "um ícone por resultado, xG como halo, o caminho da bola e onde ela cruzou a linha do gol."),
    ("Recortes da rede", "partida inteira ou até a 1ª substituição, com ou sem bola parada: quatro redes por equipe."),
    ("Jogadores", "página para cada um, jogo a jogo ou todos os jogos de uma vez, com bola × sem bola."),
    ("Mesmos dados, mesmas regras", "um motor gera o site; a soma dos passes de cada jogador fecha com o total do time."),
]
for head, body in news:
    d.ellipse([PAD, y + 10 * X, PAD + 12 * X, y + 22 * X], fill=GREEN)
    d.text((PAD + 28 * X, y), head, font=font("Bold", 23), fill=TEXT)
    y = paragraph(d, (PAD + 28 * X, y + 36 * X), body, font("Regular", 20), W - 2 * PAD - 28 * X, TEXT2, 30) + 30 * X
d.text((PAD, y + 12 * X), "github.com/LeoTaschin/Football-Inteligence-Lab", font=font("Bold", 21), fill=TEXT)
place(im, raw("players_list.png"), y + 56 * X, BOTTOM, border=False)
slides.append(im)

for i, s in enumerate(slides, start=1):
    s.save(OUT / f"etapa2_slide_{i}.png", optimize=True)
slides[0].save(OUT / "carrossel_PNSM_etapa2.pdf", save_all=True, append_images=slides[1:], resolution=144)
print("ok", sorted(p.name for p in OUT.iterdir() if p.name.startswith(("etapa2", "carrossel_PNSM_etapa2"))))
