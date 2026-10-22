import { describe, expect, it } from "vitest";

import type { NetworkCut, TeamData } from "../types/data";
import { cutKey, networkOf } from "./network";

const cut = (completed: number) => ({ completed, nodes: [], edges: [], pairs: [] }) as unknown as NetworkCut;
// the final's Italy, reduced to what networkOf reads
const italy = {
  passes: { completed: 243 },
  nodes: [],
  edges: [],
  pairs: [],
  cuts: { firstSub: cut(193), openPlay: cut(189), firstSubOpen: cut(148) },
} as unknown as TeamData;

describe("network cuts", () => {
  it("maps period × open play to the exported cut", () => {
    expect(cutKey(false, false)).toBe("full");
    expect(cutKey(false, true)).toBe("openPlay");
    expect(cutKey(true, false)).toBe("firstSub");
    expect(cutKey(true, true)).toBe("firstSubOpen");
  });

  it("draws the exported numbers of each cut", () => {
    const keys = [cutKey(false, false), cutKey(true, false), cutKey(false, true), cutKey(true, true)];
    expect(keys.map((k) => networkOf(italy, k).completed)).toEqual([243, 193, 189, 148]);
    expect(networkOf(italy, "full").nodes).toBe(italy.nodes);
  });
});
