"""Automatic label placement (CLAUDE.md 7.4).

Greedy: biggest circles first; for each one try below, above, right, left and keep
the side whose label box overlaps least with every circle and the labels already
placed (and stays inside the pitch). Ties keep that preference order, so a free
node always gets "below".

All geometry is in screen px for a pitch drawn ``width_px`` wide.
"""

from __future__ import annotations

from dataclasses import dataclass

SIDES = ("below", "above", "right", "left")

PITCH_WIDTH_PX = 560.0  # reference width of the match pitch in the design
FONT_CHAR_PX = 7.0  # average width of a 12px/600 Inter character
LABEL_HEIGHT_PX = 15.0


@dataclass(frozen=True)
class LabelTarget:
    key: object
    x: float  # pitch units (0..120)
    y: float  # pitch units (0..80)
    r: float  # circle radius in px
    text: str


Box = tuple[float, float, float, float]  # left, top, right, bottom


def node_radius_px(passes: int, max_passes: int) -> float:
    """Node radius on the 560 px pitch: ``7 + 12 * sqrt(passes / max)``."""
    return 7 + 12 * (passes / max_passes) ** 0.5 if max_passes else 7.0


def _label_box(cx: float, cy: float, r: float, w: float, side: str) -> Box:
    h = LABEL_HEIGHT_PX
    if side == "below":
        return cx - w / 2, cy + r + 2, cx + w / 2, cy + r + 2 + h
    if side == "above":
        return cx - w / 2, cy - r - 3 - h, cx + w / 2, cy - r - 3
    if side == "right":
        return cx + r + 5, cy - h / 2, cx + r + 5 + w, cy + h / 2
    return cx - r - 5 - w, cy - h / 2, cx - r - 5, cy + h / 2


def _overlap(a: Box, b: Box) -> float:
    w = min(a[2], b[2]) - max(a[0], b[0])
    h = min(a[3], b[3]) - max(a[1], b[1])
    return w * h if w > 0 and h > 0 else 0.0


def _outside(box: Box, width: float, height: float) -> float:
    inside = _overlap(box, (0, 0, width, height))
    return (box[2] - box[0]) * (box[3] - box[1]) - inside


def place_labels(targets: list[LabelTarget], width_px: float = PITCH_WIDTH_PX) -> dict[object, str]:
    scale = width_px / 120
    height_px = 80 * scale
    centers = {t.key: (t.x * scale, t.y * scale) for t in targets}
    circles = {t.key: (centers[t.key][0] - t.r, centers[t.key][1] - t.r,
                       centers[t.key][0] + t.r, centers[t.key][1] + t.r) for t in targets}

    placed: list[Box] = []
    sides: dict[object, str] = {}
    for t in sorted(targets, key=lambda t: -t.r):
        cx, cy = centers[t.key]
        w = len(t.text) * FONT_CHAR_PX

        def cost(side: str) -> float:
            box = _label_box(cx, cy, t.r, w, side)
            hits = sum(_overlap(box, c) for k, c in circles.items() if k != t.key)
            hits += sum(_overlap(box, p) for p in placed)
            return hits + 2 * _outside(box, width_px, height_px)

        best = min(SIDES, key=cost)  # min keeps the first side on ties
        sides[t.key] = best
        placed.append(_label_box(cx, cy, t.r, w, best))
    return sides
