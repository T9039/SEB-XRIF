export interface Health {
  status: string;
  model_loaded: boolean;
  model_version: string;
}

export interface Metrics {
  model: string;
  model_version: string;
  created_utc: string;
  metrics: Record<string, unknown>;
}

export interface Importance {
  native?: {
    available: boolean;
    importance?: Record<string, number>;
    reason?: string;
  };
  shap?: {
    available: boolean;
    mean_abs_shap?: Record<string, number>;
    reason?: string;
  };
}

export interface Trends {
  total_records: number;
  class_counts: Record<string, number>;
  behaviour_by_class: Record<string, Record<string, number>>;
  by_topic: Record<string, Record<string, number>>;
}

export interface PredictionRequest {
  gender: string;
  NationalITy: string;
  PlaceofBirth: string;
  StageID: string;
  GradeID: string;
  SectionID: string;
  Topic: string;
  Semester: string;
  Relation: string;
  ParentAnsweringSurvey: string;
  ParentschoolSatisfaction: string;
  StudentAbsenceDays: string;
  raisedhands: number;
  VisITedResources: number;
  AnnouncementsView: number;
  Discussion: number;
}

export interface PredictionResponse {
  prediction: string;
  probabilities: Record<string, number>;
  confidence: number;
}

export interface LearnerOptions {
  data_source: string;
  options: Record<string, string[]>;
}

export interface LearnerPage {
  data_source: string;
  total: number;
  limit: number;
  offset: number;
  rows: Record<string, string | number>[];
}

export interface ResultRow {
  model: string;
  status: string;
  accuracy: number | null;
  precision_macro: number | null;
  recall_macro: number | null;
  f1_macro: number | null;
  f1_weighted: number | null;
  roc_auc_ovr: number | null;
  cv_mean: number | null;
  cv_std: number | null;
  fit_seconds: number | null;
}

export interface ResultsPayload {
  results: ResultRow[];
  tuning: Record<string, unknown> | null;
  explain: Record<string, unknown> | null;
  evaluation: Record<string, unknown> | null;
}

export interface DiagnosticsPayload {
  data_source: string;
  folds: number;
  classes: string[];
  macro_auc: number;
  auc: Record<string, number>;
  average_precision: Record<string, number>;
  brier: Record<string, number>;
  roc: Record<string, number>[];
  pr: Record<string, number>[];
  calibration: Record<string, number>[];
  learning: Record<string, number>[];
}

export interface ColumnInfo {
  name: string;
  kind: "categorical" | "numeric";
  options?: string[];
  min?: number;
  max?: number;
  mean?: number;
}

export interface ColumnsPayload {
  data_source: string;
  target: string;
  columns: ColumnInfo[];
}

export interface AnalyticsQueryResult {
  data_source: string;
  x: string;
  y: string | null;
  group: string | null;
  aggregate: string;
  series: string[];
  rows: Record<string, string | number | null>[];
  total: number;
}

export interface SavedChartView {
  id: number;
  name: string;
  spec: Record<string, unknown>;
}

export interface EmbeddingPayload {
  data_source: string;
  n_clusters: number;
  explained_variance: number[];
  points: { x: number; y: number; tier: string; cluster: number }[];
  profiles: Record<string, string | number>[];
  clusters: string[];
}

export interface PdpPayload {
  data_source: string;
  feature: string;
  classes: string[];
  rows: Record<string, number>[];
}

export interface CorrelationPayload {
  data_source: string;
  columns: string[];
  matrix: number[][];
}

export interface XrPilot {
  name: string;
  filename: string;
  url: string;
  licence: string;
  doi: string;
  description: string;
  available: boolean;
}

export interface XrPilotsPayload {
  licence: string;
  doi: string;
  pilots: XrPilot[];
}

export interface XrTrends {
  pilot: string;
  description: string;
  licence: string;
  doi: string;
  events: number;
  learners: number;
  first_seen: string;
  last_seen: string;
  period_start: string[];
  events_by_period: number[];
  active_learners_by_period: number[];
  verb_counts: Record<string, number>;
  top_objects: { name: string; count: number }[];
}
