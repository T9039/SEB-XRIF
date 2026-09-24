import { describe, expect, it } from "vitest";
import { boxStats, normalize, numericKeys } from "./data";
import { chartConfig, PALETTE, seriesColor } from "./color";

describe("numericKeys", () => {
  it("returns only numeric value keys, excluding the axis", () => {
    const rows = [
      { x: "a", a: 1, b: 2, c: "text" },
      { x: "b", a: 3, b: 4, c: "more" },
    ];
    expect(numericKeys(rows)).toEqual(["a", "b"]);
  });
});

describe("boxStats", () => {
  it("computes the five-number summary", () => {
    const stats = boxStats([1, 2, 3, 4, 5]);
    expect(stats).toEqual({ min: 1, q1: 2, median: 3, q3: 4, max: 5 });
  });

  it("handles empty input", () => {
    expect(boxStats([])).toEqual({ min: 0, q1: 0, median: 0, q3: 0, max: 0 });
  });
});

describe("normalize", () => {
  it("scales and clamps into 0-1", () => {
    expect(normalize(5, 0, 10)).toBe(0.5);
    expect(normalize(20, 0, 10)).toBe(1);
    expect(normalize(-5, 0, 10)).toBe(0);
    expect(normalize(5, 5, 5)).toBe(0);
  });
});

describe("chartConfig / colors", () => {
  it("assigns palette colours and default labels", () => {
    const config = chartConfig(["L", "M", "H"]);
    expect(config.L.color).toBe(PALETTE[0]);
    expect(config.M.color).toBe(PALETTE[1]);
    expect(config.H.label).toBe("H");
  });

  it("honours custom labels and cycles the palette", () => {
    const config = chartConfig(["a", "b"], { a: "Alpha" });
    expect(config.a.label).toBe("Alpha");
    expect(seriesColor(PALETTE.length)).toBe(PALETTE[0]);
  });
});
