"""Shared drawing helpers for the LinkedIn slides (1080x1350 drawn at 2x)."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

X = 2  # render scale
W, H, PAD = 1080 * X, 1350 * X, 56 * X
TEXT, TEXT2, MUTED, BORDER, GREEN = "#0A0A0B", "#3F3F46", "#6B6B73", "#E4E4E7", "#009C3B"


FONTS = Path(".")  # set by the script: layout.FONTS = Path(...)


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


def slide(page: int, total: int, title: str, subtitle: str, kicker: str = "F.I.L · PROJETO 01 · PNSM"):
    im = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(im)
    d.text((PAD, PAD), kicker, font=font("SemiBold", 14), fill=MUTED)
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
