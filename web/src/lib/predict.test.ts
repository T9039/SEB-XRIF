import { describe, expect, it } from "vitest";
import { predictionRows } from "./predict";

describe("predictionRows", () => {
  it("sorts probabilities most-likely first", () => {
    const rows = predictionRows({ L: 0.1, M: 0.7, H: 0.2 });
    expect(rows.map((row) => row.label)).toEqual(["M", "H", "L"]);
    expect(rows[0].percent).toBe(70);
  });

  it("handles an empty map", () => {
    expect(predictionRows({})).toEqual([]);
  });
});
