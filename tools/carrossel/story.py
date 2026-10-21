"""Instagram story (1080x1920 drawn at 2x). Usage: story.py <raw> <fonts> <out_png>

Title, subtitle, the final's pass network (Gérson selected), the players' movement
(with × without the ball) and the campaign numbers. Top ~150 px and bottom ~160 px
stay free for Instagram's header and reply bar.
"""

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

RAW, FONTS, OUT = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
X = 2
W, H, PAD = 1080 * X, 1920 * X, 72 * X
TEXT, TEXT2, MUTED, BORDER, GREEN = "#0A0A0B", "#3F3F46", "#6B6B73", "#E4E4E7", "#009C3B"
SAFE_TOP, SAFE_BOTTOM = 160 * X, H - 160 * X


def font(weight, px):
    return ImageFont.truetype(str(FONTS / f"Inter-{weight}.ttf"), px * X)


def wrap(d, text, fnt, width):
    lines, line = [], ""
    for word in text.split():
        trial = f"{line} {word}".strip()
        if d.textlength(trial, font=fnt) <= width or not line:
            line = trial
        else:
            lines.append(line)
            line = word
    return lines + [line]


def paragraph(d, x, y, text, fnt, width, color, lh):
    for ln in wrap(d, text, fnt, width):
        d.text((x, y), ln, font=fnt, fill=color)
        y += lh * X
    return y


def pitch(im, d, name, y, title, caption, width):
    img = Image.open(RAW / name).convert("RGB")
    img = img.resize((width, round(img.height * width / img.width)), Image.LANCZOS)
    x = (W - width) // 2
    im.paste(img, (x, y))
    d.rectangle([x - X, y - X, x + img.width, y + img.height], outline=BORDER, width=X)
    y += img.height + 14 * X
    d.text((x, y), title, font=font("Bold", 25), fill=TEXT)
    d.text((x, y + 34 * X), caption, font=font("Regular", 22), fill=MUTED)
    return y + 66 * X


im = Image.new("RGB", (W, H), "white")
d = ImageDraw.Draw(im)

y = SAFE_TOP + 10 * X
d.rounded_rectangle([PAD, y + 6 * X, PAD + 14 * X, y + 20 * X], radius=7 * X, fill=GREEN)
d.text((PAD + 26 * X, y), "F.I.L · FOOTBALL INTELLIGENCE LAB", font=font("Bold", 21), fill=MUTED)
y += 46 * X
y = paragraph(d, PAD, y, "Como o Brasil de 1970 trocava a bola", font("ExtraBold", 66), W - 2 * PAD, TEXT, 72)
y += 14 * X
y = paragraph(d, PAD, y, "Redes de passes e movimentação dos jogadores na campanha do tri, com dados reais de cada partida.",
              font("Regular", 28), W - 2 * PAD, TEXT2, 38)

MAP_W = 720 * X
y += 22 * X
y = pitch(im, d, "net_gerson.png", y, "Rede de passes · final de 1970",
          "Gérson: 70 passes completos, 26 para Carlos Alberto", MAP_W)
y += 4 * X
y = pitch(im, d, "phases_def.png", y, "Movimentação · com bola × sem bola",
          "sem a bola, o time recua 16,5 m; Carlos Alberto, 34 m", MAP_W)

# campaign numbers
y += 8 * X
d.line([(PAD, y), (W - PAD, y)], fill=BORDER, width=X)
stats = [("6 de 6", "vitórias"), ("2.490", "passes completos"), ("19", "gols")]
col = (W - 2 * PAD) // 3
for i, (value, label) in enumerate(stats):
    x = PAD + i * col
    d.text((x, y + 18 * X), value, font=font("ExtraBold", 46), fill=TEXT)
    d.text((x, y + 76 * X), label, font=font("Regular", 21), fill=MUTED)
y += 116 * X
d.text((W - PAD, y), "Dados: StatsBomb Open Data · Leonardo Taschin", font=font("Regular", 19), fill=MUTED, anchor="ra")
y += 26 * X

assert y <= SAFE_BOTTOM, f"content ends at {y // X}px, below the safe area ({SAFE_BOTTOM // X}px)"
im.save(OUT, optimize=True)
print(OUT, "content ends at", y // X, "px of", H // X)
