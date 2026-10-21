import { describe, expect, it } from "vitest";

import { formatClock, formatDate, formatDecimal, formatInt, formatPercent } from "./format";

describe("format", () => {
  it("uses pt-BR separators", () => {
    expect(formatInt(2490)).toBe("2.490");
    expect(formatDecimal(14.75)).toBe("14,75");
    expect(formatDecimal(2.7, 2)).toBe("2,70");
  });

  it("formats percentages and dates", () => {
    expect(formatPercent(400, 471)).toBe("85%");
    expect(formatPercent(1, 0)).toBe("–");
    expect(formatDate("1970-06-21")).toBe("21 jun 1970");
  });

  it("formats the replay clock", () => {
    expect(formatClock(7.4)).toBe("0:07");
    expect(formatClock(29.9)).toBe("0:29");
  });
});
