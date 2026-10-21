// Visual scales from CLAUDE.md 7.4. Everything is drawn in StatsBomb units
// (viewBox 0 0 120 80, y grows downward like SVG). Sizes are specified in px for a
// 560 px-wide pitch and converted with PX, so they scale with the pitch.

import type { LabelSide } from "../types/data";

export const PITCH_W = 120;
export const PITCH_H = 80;
export const REFERENCE_WIDTH_PX = 560;
/** One design pixel in pitch units (on the 560 px reference pitch). */
export const PX = PITCH_W / REFERENCE_WIDTH_PX;

export interface XY {
  x: number;
  y: number;
}

/** Node radius in px: 7 + 12·√(passes / max). */
export function nodeRadius(passes: number, maxPasses: number): number {
  return 7 + 12 * Math.sqrt(maxPasses > 0 ? Math.max(0, passes) / maxPasses : 0);
}

/** Undirected line: width 1 + 8·n/max px, opacity 0.25 + 0.65·n/max (max 0.9). */
export function lineStyle(n: number, maxPair: number): { width: number; opacity: number } {
  const k = maxPair > 0 ? n / maxPair : 0;
  return { width: 1 + 8 * k, opacity: Math.min(0.9, 0.25 + 0.65 * k) };
}

/** Directed arrow width in px: 1.5 + 6·n/maxDirected. */
export function arrowWidth(n: number, maxDirected: number): number {
  return 1.5 + 6 * (maxDirected > 0 ? n / maxDirected : 0);
}

export interface ArrowShape {
  /** shaft + head as one polygon, in pitch units */
  points: XY[];
  length: number;
}

/**
 * Arrow from node A to node B (pitch units; radii and width in px).
 * Offset perpendicular by 2 + w/2 px so A→B and B→A sit side by side, shortened by
 * the node radii, head 7 + 1.2w long and 3.5 + 0.9w half-wide. Null if too short.
 */
export function arrowShape(a: XY, b: XY, rA: number, rB: number, widthPx: number): ArrowShape | null {
  const dx = b.x - a.x;
  const dy = b.y - a.y;
  const d = Math.hypot(dx, dy);
  if (d < 1e-6) return null;
  const ux = dx / d;
  const uy = dy / d;
  const px = -uy;
  const py = ux;

  const off = (2 + widthPx / 2) * PX;
  const start = { x: a.x + ux * (rA + 1) * PX + px * off, y: a.y + uy * (rA + 1) * PX + py * off };
  const end = { x: b.x - ux * (rB + 2) * PX + px * off, y: b.y - uy * (rB + 2) * PX + py * off };
  // signed: negative when the circles overlap (start would be past end)
  const length = d - (rA + rB + 3) * PX;

  const headLen = (7 + 1.2 * widthPx) * PX;
  const headHalf = (3.5 + 0.9 * widthPx) * PX;
  if (length < headLen + 3 * PX) return null;

  const half = (widthPx / 2) * PX;
  const neck = { x: end.x - ux * headLen, y: end.y - uy * headLen };
  const at = (p: XY, s: number) => ({ x: p.x + px * s, y: p.y + py * s });
  return {
    points: [at(start, half), at(neck, half), at(neck, headHalf), end, at(neck, -headHalf), at(neck, -half), at(start, -half)],
    length,
  };
}

export function polygonPoints(points: XY[]): string {
  return points.map((p) => `${round(p.x)},${round(p.y)}`).join(" ");
}

export interface LabelPlacement {
  x: number;
  y: number;
  anchor: "start" | "middle" | "end";
  baseline: "hanging" | "auto" | "central";
}

/** Where to draw a node label for the side chosen by the engine (radius in px). */
export function labelPlacement(center: XY, radiusPx: number, side: LabelSide): LabelPlacement {
  switch (side) {
    case "above":
      return { x: center.x, y: center.y - (radiusPx + 3) * PX, anchor: "middle", baseline: "auto" };
    case "left":
      return { x: center.x - (radiusPx + 5) * PX, y: center.y, anchor: "end", baseline: "central" };
    case "right":
      return { x: center.x + (radiusPx + 5) * PX, y: center.y, anchor: "start", baseline: "central" };
    default:
      return { x: center.x, y: center.y + (radiusPx + 2) * PX, anchor: "middle", baseline: "hanging" };
  }
}

/** Linear interpolation along a segment, t clamped to [0, 1]. */
export function lerp(a: XY, b: XY, t: number): XY {
  const k = Math.min(1, Math.max(0, t));
  return { x: a.x + (b.x - a.x) * k, y: a.y + (b.y - a.y) * k };
}

function round(v: number): number {
  return Math.round(v * 100) / 100;
}
