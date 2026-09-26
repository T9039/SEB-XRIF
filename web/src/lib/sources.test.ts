import { describe, expect, it } from "vitest";
import {
  DATA_SOURCES,
  DEFAULT_SOURCE_ID,
  FEATURE_MAPPING,
  getSource,
  isXrSource,
  mergeSources,
} from "./sources";

describe("data sources", () => {
  it("lists the LMS prototype and the five ARETE pilots", () => {
    expect(DATA_SOURCES.map((source) => source.id)).toEqual([
      "kalboard",
      "pbis",
      "english-literacy",
      "stem-geometry",
      "stem-geography",
      "lxd",
    ]);
    expect(DATA_SOURCES.filter((source) => source.kind === "lms")).toHaveLength(1);
    expect(DATA_SOURCES.filter((source) => source.kind === "xr")).toHaveLength(5);
  });

  it("classifies XR sources", () => {
    expect(isXrSource("pbis")).toBe(true);
    expect(isXrSource(DEFAULT_SOURCE_ID)).toBe(false);
  });

  it("falls back to the default for an unknown id", () => {
    expect(getSource("does-not-exist").id).toBe(DEFAULT_SOURCE_ID);
  });
});

describe("mergeSources", () => {
  it("adds uploaded sources as generic and keeps the built-ins", () => {
    const merged = mergeSources([
      { name: "kalboard", kind: "builtin", description: "" },
      { name: "my-upload", kind: "upload", description: "demo" },
    ]);
    expect(merged.map((entry) => entry.id)).toContain("my-upload");
    expect(merged.map((entry) => entry.id)).toContain("kalboard");
    expect(merged.filter((entry) => entry.id === "kalboard")).toHaveLength(1);
    expect(merged.find((entry) => entry.id === "my-upload")?.kind).toBe("generic");
    expect(merged.find((entry) => entry.id === "my-upload")?.label).toContain("my-upload");
  });
});

describe("LMS to XR feature mapping", () => {
  it("maps every LMS feature to an XR analogue and verbs", () => {
    expect(FEATURE_MAPPING.length).toBeGreaterThan(0);
    for (const row of FEATURE_MAPPING) {
      expect(row.lms).toBeTruthy();
      expect(row.xr).toBeTruthy();
      expect(row.verbs.length).toBeGreaterThan(0);
    }
  });

  it("covers the documented Kalboard features", () => {
    expect(FEATURE_MAPPING.map((row) => row.lms)).toEqual([
      "raisedhands",
      "VisITedResources",
      "AnnouncementsView",
      "Discussion",
      "StudentAbsenceDays",
    ]);
  });
});
