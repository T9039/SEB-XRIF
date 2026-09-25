export type SourceKind = "lms" | "xr";

export interface DataSource {
  id: string;
  kind: SourceKind;
  label: string;
  description: string;
}

export interface FeatureMapping {
  lms: string;
  xr: string;
  verbs: string[];
}

export const DEFAULT_SOURCE_ID = "kalboard";

/** Every dataset the dashboard can point at, LMS and XR. */
export const DATA_SOURCES: DataSource[] = [
  {
    id: "kalboard",
    kind: "lms",
    label: "Kalboard 360 (LMS, non-XR)",
    description: "K-12 LMS data; prototypes the analytics and support-band pipeline.",
  },
  {
    id: "pbis",
    kind: "xr",
    label: "ARETE PBIS (AR)",
    description: "Positive Behaviour Intervention and Support AR lessons.",
  },
  {
    id: "english-literacy",
    kind: "xr",
    label: "ARETE English Literacy (AR)",
    description: "English literacy AR modules.",
  },
  {
    id: "stem-geometry",
    kind: "xr",
    label: "ARETE STEM Geometry (AR)",
    description: "STEM geometry AR activities.",
  },
  {
    id: "stem-geography",
    kind: "xr",
    label: "ARETE STEM Geography (AR)",
    description: "STEM geography AR activities.",
  },
  {
    id: "lxd",
    kind: "xr",
    label: "ARETE LXD (AR)",
    description: "Teachers authoring AR learning resources.",
  },
];

/** The LMS feature to XR analogue mapping shown in the dashboard. */
export const FEATURE_MAPPING: FeatureMapping[] = [
  { lms: "raisedhands", xr: "in-VR help requests", verbs: ["responded", "selected"] },
  {
    lms: "VisITedResources",
    xr: "VR/AR content interactions",
    verbs: ["accessed", "found"],
  },
  { lms: "AnnouncementsView", xr: "task briefings read", verbs: ["read"] },
  { lms: "Discussion", xr: "collaborative VR activity", verbs: ["joined"] },
  {
    lms: "StudentAbsenceDays",
    xr: "session attendance / drop-off",
    verbs: ["started", "left"],
  },
];

export function getSource(id: string): DataSource {
  return DATA_SOURCES.find((source) => source.id === id) ?? DATA_SOURCES[0];
}

export function isXrSource(id: string): boolean {
  return getSource(id).kind === "xr";
}
