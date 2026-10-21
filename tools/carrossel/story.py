"""Instagram story (1080x1920 drawn at 2x). Usage: story.py <raw> <fonts> <out_png>"""

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

RAW, FONTS, OUT = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
X = 2
W, H, PAD = 1080 * X, 1920 * X, 72 * X
TEXT, TEXT2, MUTED, BORDER = "#0A0A0B", "#3F3F46", "#6B6B73", "#E4E4E7"
YELLOW, GREEN = "#FFD500", "#009C3B"


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


im = Image.new("RGB", (W, H), "white")
d = ImageDraw.Draw(im)

# top ~170 px is covered by the story header: start below it
y = 190 * X
d.rounded_rectangle([PAD, y, PAD + 14 * X, y + 14 * X], radius=7 * X, fill=GREEN)
d.text((PAD + 26 * X, y - 6 * X), "NO AR · F.I.L · PROJETO 01", font=font("Bold", 22), fill=MUTED)
y += 50 * X
y = paragraph(d, PAD, y, "Como o Brasil de 1970 trocava a bola", font("ExtraBold", 78), W - 2 * PAD, TEXT, 84)
y += 18 * X
y = paragraph(d, PAD, y, "Redes de passes, posições com e sem bola e o replay dos gols da campanha do tri. Com dados reais.",
              font("Regular", 30), W - 2 * PAD, TEXT2, 41)

# main visual: Gérson selected in the final
y += 34 * X
net = Image.open(RAW / "net_gerson.png").convert("RGB")
k = (W - 2 * PAD) / net.width
net = net.resize((W - 2 * PAD, round(net.height * k)), Image.LANCZOS)
im.paste(net, (PAD, y))
d.rectangle([PAD - X, y - X, PAD + net.width, y + net.height], outline=BORDER, width=X)
y += net.height + 18 * X
d.text((PAD, y), "Final de 1970 · clique em um jogador", font=font("Bold", 26), fill=TEXT)
d.text((PAD, y + 36 * X), "Gérson: 70 passes, 26 para Carlos Alberto", font=font("Regular", 23), fill=MUTED)
d.text((W - PAD, y + 36 * X), "Dados: StatsBomb Open Data", font=font("Regular", 20), fill=MUTED, anchor="ra")

# numbers
y += 96 * X
d.line([(PAD, y), (W - PAD, y)], fill=BORDER, width=X)
stats = [("6", "jogos"), ("2.490", "passes completos"), ("19", "gols")]
col = (W - 2 * PAD) // 3
for i, (value, label) in enumerate(stats):
    x = PAD + i * col
    d.text((x, y + 22 * X), value, font=font("ExtraBold", 58), fill=TEXT)
    d.text((x, y + 94 * X), label, font=font("Regular", 23), fill=MUTED)
y += 140 * X
d.line([(PAD, y), (W - PAD, y)], fill=BORDER, width=X)

# call to action, pointing at the link sticker area just below
y += 36 * X
box_h = 108 * X
d.rounded_rectangle([PAD, y, W - PAD, y + box_h], radius=20 * X, fill=TEXT)
d.text((PAD + 40 * X, y + box_h // 2), "Explore o site", font=font("ExtraBold", 44), fill="white", anchor="lm")
d.ellipse([W - PAD - 36 * X - 68 * X, y + 20 * X, W - PAD - 36 * X, y + 88 * X], fill=YELLOW)
d.text((W - PAD - 36 * X - 34 * X, y + box_h // 2 + 2 * X), "↓", font=font("ExtraBold", 40), fill=TEXT, anchor="mm")
y += box_h + 18 * X
d.text((W // 2, y), "toque no link abaixo", font=font("SemiBold", 24), fill=MUTED, anchor="ma")
y += 34 * X  # below this: free space for the Instagram link sticker


im.save(OUT, optimize=True)
print(OUT, "content ends at", y // X, "px")
