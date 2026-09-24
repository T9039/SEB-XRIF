import { describe, expect, it } from "vitest";
import { toCsv } from "./export";

describe("toCsv", () => {
  it("unions keys into a header row", () => {
    const csv = toCsv([
      { x: "A", value: 1 },
      { x: "B", value: 2, extra: "z" },
    ]);
    expect(csv.split("\n")[0]).toBe("x,value,extra");
    expect(csv.split("\n")[1]).toBe("A,1,");
  });

  it("escapes commas, quotes, and newlines", () => {
    const csv = toCsv([{ x: "a,b", y: 'he said "hi"', z: "line\nbreak" }]);
    expect(csv).toContain('"a,b"');
    expect(csv).toContain('"he said ""hi"""');
    expect(csv).toContain('"line\nbreak"');
  });

  it("returns empty string for no rows", () => {
    expect(toCsv([])).toBe("");
  });
});
