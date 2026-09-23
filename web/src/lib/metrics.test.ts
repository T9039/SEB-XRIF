import { describe, expect, it } from "vitest";
import { cellIntensity, classMetrics } from "./metrics";

describe("classMetrics", () => {
  const confusion = [
    [8, 1, 1],
    [2, 10, 3],
    [0, 2, 13],
  ];
  const labels = ["L", "M", "H"];

  it("computes precision, recall, and F1 per class", () => {
    const metrics = classMetrics(confusion, labels);
    expect(metrics.map((metric) => metric.label)).toEqual(["L", "M", "H"]);

    const low = metrics[0];
    expect(low.support).toBe(10);
    expect(low.precision).toBeCloseTo(8 / 10, 5);
    expect(low.recall).toBeCloseTo(8 / 10, 5);
    expect(low.f1).toBeCloseTo(0.8, 5);

    const high = metrics[2];
    expect(high.precision).toBeCloseTo(13 / 17, 5);
    expect(high.recall).toBeCloseTo(13 / 15, 5);
  });

  it("returns zeros when a class is never predicted", () => {
    const metrics = classMetrics(
      [
        [5, 5],
        [0, 0],
      ],
      ["A", "B"],
    );
    expect(metrics[1].precision).toBe(0);
    expect(metrics[1].recall).toBe(0);
    expect(metrics[1].f1).toBe(0);
  });
});

describe("cellIntensity", () => {
  it("normalises against the maximum", () => {
    expect(cellIntensity(5, 10)).toBe(0.5);
    expect(cellIntensity(0, 0)).toBe(0);
  });
});
