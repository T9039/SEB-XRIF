import { describe, expect, it } from "vitest";
import { buildChartSpec, type StudioConfig } from "./spec";

const base: StudioConfig = {
  type: "bar",
  x: "Topic",
  y: "raisedhands",
  group: "",
  aggregate: "mean",
  source: "learners",
};

describe("buildChartSpec", () => {
  it("builds a single-series bar from scalar query rows", () => {
    const spec = buildChartSpec(base, [{ x: "IT", value: 20 }], ["value"]);
    expect(spec.rows).toEqual([{ x: "IT", value: 20 }]);
    expect(spec.series).toEqual(["value"]);
    expect(spec.showLegend).toBe(false);
  });

  it("keeps grouped series wide and stacks bars", () => {
    const spec = buildChartSpec(
      { ...base, group: "Class" },
      [{ x: "IT", L: 10, M: 20, H: 30 }],
      ["L", "M", "H"],
    );
    expect(spec.series).toEqual(["L", "M", "H"]);
    expect(spec.stacked).toBe(true);
    expect(spec.showLegend).toBe(true);
  });

  it("maps long-format chart types to name/value rows", () => {
    const spec = buildChartSpec({ ...base, type: "pie" }, [{ x: "IT", value: 20 }], ["value"]);
    expect(spec.rows).toEqual([{ name: "IT", value: 20 }]);
    expect(spec.valueKey).toBe("value");
  });
});
