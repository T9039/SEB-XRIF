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
