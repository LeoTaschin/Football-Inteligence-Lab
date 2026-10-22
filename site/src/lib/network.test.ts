import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

import type { MatchData } from "../types/data";
import { cutKey, networkOf } from "./network";

const final: MatchData = JSON.parse(readFileSync(new URL("../../public/data/matches/3888702.json", import.meta.url), "utf-8"));

describe("network cuts", () => {
  it("maps period × open play to the exported cut", () => {
    expect(cutKey(false, false)).toBe("full");
    expect(cutKey(false, true)).toBe("openPlay");
    expect(cutKey(true, false)).toBe("firstSub");
    expect(cutKey(true, true)).toBe("firstSubOpen");
  });

  it("draws the exported numbers of each cut (final, Italy)", () => {
    const italy = final.teams[1];
    expect([cutKey(false, false), cutKey(true, false), cutKey(false, true), cutKey(true, true)].map((k) => networkOf(italy, k).completed)).toEqual([
      243, 193, 189, 148,
    ]);
    expect(networkOf(italy, "full").nodes).toBe(italy.nodes);
  });
});
