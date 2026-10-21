"""Drawing blocks for the post, positioned in px like the design (origin top-left).

A transparent axes covers the whole figure in px coordinates for text and bars;
each pitch is its own axes in StatsBomb units (0..120 x 0..80, y down).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from math import sqrt

import matplotlib.pyplot as plt
from matplotlib import patheffects
from matplotlib.axes import Axes
from matplotlib.patches import Circle, FancyBboxPatch, Rectangle

from pnsm.report import theme

LABEL_HALO = [patheffects.withStroke(linewidth=3 * theme.PT, foreground=theme.SURFACE)]


@dataclass
class Run:
    """A piece of text with its own style, for rich lines ("Brasil 4 × 1 Itália")."""

    text: str
    color: str = theme.TEXT
    weight: int | str = 400


class Canvas:
    def __init__(self, width: int, height: int, family: str):
        self.w, self.h, self.family = width, height, family
        self.fig = plt.figure(figsize=(width / theme.DPI, height / theme.DPI), dpi=theme.DPI, facecolor=theme.BG)
        self.ax = self.fig.add_axes((0, 0, 1, 1), zorder=10)
        self.ax.set_xlim(0, width)
        self.ax.set_ylim(height, 0)
        self.ax.axis("off")
        self.ax.patch.set_alpha(0)
        self._renderer = self.fig.canvas.get_renderer()

    # --- text ---------------------------------------------------------------------

    def text(self, x: float, y: float, s: str, size: float, color: str = theme.TEXT, weight: int | str = 400,
             ha: str = "left", va: str = "top"):
        return self.ax.text(x, y, s, fontsize=size * theme.PT, color=color, fontweight=weight, family=self.family,
                            ha=ha, va=va)

    def measure(self, s: str, size: float, weight: int | str = 400) -> float:
        """Width in px of ``s`` at ``size`` px, counting leading/trailing spaces (matplotlib trims them)."""

        def raw(text: str) -> float:
            t = self.text(0, 0, text, size, weight=weight)
            width = t.get_window_extent(self._renderer).width
            t.remove()
            return width

        return raw(f"|{s}|") - raw("||")

    def runs(self, x: float, y: float, runs: list[Run], size: float, ha: str = "left") -> float:
        """One line of mixed styles; returns its width. Spaces at the ends of a run are kept."""
        space = self.measure(" ", size)
        pieces = []
        for r in runs:
            body = r.text.strip(" ")
            lead = len(r.text) - len(r.text.lstrip(" "))
            trail = len(r.text) - len(r.text.rstrip(" "))
            pieces.append((r, body, lead * space, self.measure(body, size, r.weight), trail * space))
        total = sum(lead + w + trail for _, _, lead, w, trail in pieces)
        cursor = x - total if ha == "right" else x
        for r, body, lead, w, trail in pieces:
            cursor += lead
            self.text(cursor, y, body, size, r.color, r.weight)
            cursor += w + trail
        return total

    def paragraph(self, x: float, y: float, runs: list[Run], size: float, max_width: float, line_height: float) -> float:
        """Word-wrapped rich text; returns the y below the last line."""
        space = self.measure(" ", size)
        # tokens keep whether a space precedes them, so "Alberto" + ": 44" stays glued
        tokens: list[tuple[str, Run, bool]] = []
        pending_space = False  # a run ending in a space separates it from the next run
        for r in runs:
            for match in re.finditer(r"(\s*)(\S+)", r.text):
                tokens.append((match.group(2), r, bool(match.group(1)) or pending_space or not tokens))
                pending_space = False
            pending_space = r.text.endswith(" ")
        lines: list[list[tuple[str, Run, float, bool]]] = []
        line: list[tuple[str, Run, float, bool]] = []
        line_w = 0.0
        for word, r, spaced in tokens:
            w = self.measure(word, size, r.weight)
            extra = w + (space if line and spaced else 0)
            if line and spaced and line_w + extra > max_width:
                lines.append(line)
                line, line_w, extra = [], 0.0, w
            line.append((word, r, w, spaced))
            line_w += extra
        if line:
            lines.append(line)
        for i, ln in enumerate(lines):
            cursor = x
            for j, (word, r, w, spaced) in enumerate(ln):
                if j and spaced:
                    cursor += space
                self.text(cursor, y + i * line_height, word, size, r.color, r.weight)
                cursor += w
        return y + len(lines) * line_height

    # --- shapes -------------------------------------------------------------------

    def rect(self, x: float, y: float, w: float, h: float, color: str, radius: float = 0):
        if radius:
            patch = FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={radius}",
                                   facecolor=color, edgecolor="none", mutation_aspect=1)
        else:
            patch = Rectangle((x, y), w, h, facecolor=color, edgecolor="none")
        self.ax.add_patch(patch)

    def hline(self, x: float, y: float, w: float, color: str = theme.BORDER):
        self.ax.plot([x, x + w], [y, y], color=color, linewidth=1 * theme.PT, solid_capstyle="butt")

    def dot(self, cx: float, cy: float, r: float, fill: str, ring: str | None = None, ring_px: float = 2):
        self.ax.add_patch(Circle((cx, cy), r, facecolor=fill, edgecolor=ring or "none",
                                 linewidth=ring_px * theme.PT if ring else 0))

    def pitch(self, x: float, y: float, w: float, h: float) -> Axes:
        """Pitch axes at (x, y) px, w × h px, drawn in StatsBomb units."""
        ax = self.fig.add_axes((x / self.w, 1 - (y + h) / self.h, w / self.w, h / self.h), zorder=5)
        ax.set_xlim(0, 120)
        ax.set_ylim(80, 0)
        ax.set_aspect("equal")
        ax.axis("off")
        draw_markings(ax)
        return ax

    def save(self, path) -> None:
        self.fig.savefig(path, dpi=theme.DPI, facecolor=theme.BG)
        plt.close(self.fig)


def draw_markings(ax: Axes) -> None:
    """Same markings as the site's <Pitch/>."""
    lw = 1 * theme.PT
    style = dict(fill=False, edgecolor=theme.LINE, linewidth=lw)
    ax.add_patch(Rectangle((0, 0), 120, 80, facecolor=theme.SURFACE, edgecolor=theme.LINE, linewidth=lw, zorder=0))
    ax.plot([60, 60], [0, 80], color=theme.LINE, linewidth=lw, zorder=1)
    ax.add_patch(Circle((60, 40), 10, zorder=1, **style))
    for rx, ry, rw, rh in [(0, 18, 18, 44), (0, 30, 6, 20), (102, 18, 18, 44), (114, 30, 6, 20)]:
        ax.add_patch(Rectangle((rx, ry), rw, rh, zorder=1, **style))


def draw_network(ax: Axes, team: dict, width_px: float, max_passes: int, max_pair: int, min_pair: int,
                 family: str) -> None:
    """Undirected pass network of one team (export JSON shape) on a pitch ``width_px`` wide.

    Scales from the post design: radius 6 + 10·√(passes/max) px, line 1 + 7·n/max px.
    """
    u = 120 / width_px  # pitch units per px
    by_id = {n["playerId"]: n for n in team["nodes"]}
    colors = team["colors"]

    for p in sorted((p for p in team["pairs"] if p["n"] >= min_pair), key=lambda p: p["n"]):
        a, b = by_id[p["a"]]["ball"], by_id[p["b"]]["ball"]
        k = p["n"] / max_pair
        ax.plot([a["x"], b["x"]], [a["y"], b["y"]], color=colors["line"], alpha=min(0.9, 0.25 + 0.65 * k),
                linewidth=(1 + 7 * k) * theme.PT, solid_capstyle="round", zorder=2)

    for n in team["nodes"]:
        x, y = n["ball"]["x"], n["ball"]["y"]
        r = 6 + 10 * sqrt(n["passes"] / max_passes)
        ax.add_patch(Circle((x, y), (r + 2) * u, facecolor=theme.SURFACE, edgecolor="none", zorder=3))
        ax.add_patch(Circle((x, y), r * u, facecolor=colors["fill"], edgecolor=colors["line"],
                            linewidth=2 * theme.PT, zorder=4))
        if n["num"] is not None:
            ax.text(x, y, str(n["num"]), fontsize=(8 + r * 0.3) * theme.PT, fontweight=800, color=colors["ink"],
                    ha="center", va="center_baseline", family=family, zorder=5)
        lx, ly, ha, va = _label_spot(x, y, r, n["label"], u)
        ax.text(lx, ly, n["name"], fontsize=11 * theme.PT, fontweight=600, color=theme.TEXT, ha=ha, va=va,
                family=family, zorder=6, path_effects=LABEL_HALO)

    ax.text(120 - 8 * u, 80 - 6 * u, "ATAQUE →", fontsize=11 * theme.PT, fontweight=600, color=theme.TEXT_MUTED,
            ha="right", va="bottom", family=family, zorder=6)


def _label_spot(x: float, y: float, r: float, side: str, u: float):
    if side == "above":
        return x, y - (r + 3) * u, "center", "bottom"
    if side == "left":
        return x - (r + 4) * u, y, "right", "center"
    if side == "right":
        return x + (r + 4) * u, y, "left", "center"
    return x, y + (r + 2) * u, "center", "top"
