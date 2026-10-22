import { describe, expect, it } from "vitest";

import { arrowShape, arrowWidth, labelPlacement, lerp, lineStyle, nodeRadius, PX, shotPoint, shotRadius } from "./geometry";

describe("scales (CLAUDE.md 7.4)", () => {
  it("node radius goes from 7 to 19 px", () => {
    expect(nodeRadius(0, 70)).toBe(7);
    expect(nodeRadius(70, 70)).toBe(19);
    expect(nodeRadius(35, 70)).toBeCloseTo(7 + 12 * Math.SQRT1_2);
  });

  it("line width and opacity follow the pair count", () => {
    expect(lineStyle(44, 44)).toEqual({ width: 9, opacity: 0.9 });
    expect(lineStyle(0, 44).opacity).toBe(0.25);
  });

  it("arrow width", () => {
    expect(arrowWidth(26, 26)).toBe(7.5);
    expect(arrowWidth(0, 26)).toBe(1.5);
  });
});

describe("arrowShape", () => {
  const a = { x: 20, y: 40 };
  const b = { x: 80, y: 40 };

  it("ends before the target node and points at it", () => {
    const shape = arrowShape(a, b, 10, 10, 3)!;
    const tip = shape.points[3];
    expect(tip.x).toBeCloseTo(80 - 12 * PX);
    expect(shape.points[0].x).toBeCloseTo(20 + 11 * PX);
  });

  it("A→B and B→A are offset to opposite sides", () => {
    const ab = arrowShape(a, b, 10, 10, 3)!;
    const ba = arrowShape(b, a, 10, 10, 3)!;
    // y grows downward: A→B (to the right) sits below the axis, B→A above it
    expect(ab.points[3].y).toBeGreaterThan(40);
    expect(ba.points[3].y).toBeLessThan(40);
  });

  it("is null when nodes overlap", () => {
    expect(arrowShape(a, { x: 21, y: 40 }, 10, 10, 3)).toBeNull();
    expect(arrowShape(a, a, 10, 10, 3)).toBeNull();
  });
});

describe("labelPlacement", () => {
  it("places labels outside the circle on the chosen side", () => {
    const c = { x: 60, y: 40 };
    expect(labelPlacement(c, 10, "below")).toMatchObject({ x: 60, anchor: "middle", baseline: "hanging" });
    expect(labelPlacement(c, 10, "below").y).toBeCloseTo(40 + 12 * PX);
    expect(labelPlacement(c, 10, "left")).toMatchObject({ anchor: "end", y: 40 });
    expect(labelPlacement(c, 10, "right").x).toBeCloseTo(60 + 15 * PX);
  });
});

describe("lerp", () => {
  it("clamps t", () => {
    expect(lerp({ x: 0, y: 0 }, { x: 10, y: 20 }, 0.5)).toEqual({ x: 5, y: 10 });
    expect(lerp({ x: 0, y: 0 }, { x: 10, y: 20 }, 2)).toEqual({ x: 10, y: 20 });
  });
});

describe("shot map", () => {
  it("marker area is proportional to xG, with a floor", () => {
    expect(shotRadius(0.8)).toBe(22);
    expect(shotRadius(0.2)).toBeCloseTo(11); // a quarter of the xG, half the radius
    expect(shotRadius(0.001)).toBe(3.5);
    expect(shotRadius(null)).toBe(3.5); // missing xG is drawn, never as zero xG
  });

  it("turns the pitch so the team attacks upward", () => {
    expect(shotPoint(120, 40)).toEqual({ x: 40, y: 0 }); // centre of the goal, top
    expect(shotPoint(108, 80)).toEqual({ x: 80, y: 12 }); // right touchline on the right
  });
});
