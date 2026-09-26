import { useMutation, useQuery } from "@tanstack/react-query";
import { api } from "./client";
import type {
  AnalyticsQueryResult,
  ColumnsPayload,
  CorrelationPayload,
  DatasetList,
  DiagnosticsPayload,
  EmbeddingPayload,
  EvaluationPayload,
  Health,
  Importance,
  LearnerOptions,
  LearnerPage,
  Metrics,
  ModelFeatures,
  PredictionRequest,
  PredictionResponse,
  ResultsPayload,
  PdpPayload,
  SavedChartView,
  Trends,
  XrPilotsPayload,
  XrRisk,
  XrLearnerPage,
  XrTrends,
} from "../types";

export function useHealth() {
  return useQuery({
    queryKey: ["health"],
    queryFn: async () => (await api.get<Health>("/health")).data,
  });
}

export function useTrends() {
  return useQuery({
    queryKey: ["trends"],
    queryFn: async () => (await api.get<Trends>("/trends")).data,
  });
}

export function useMetrics(source = "kalboard") {
  return useQuery({
    queryKey: ["metrics", source],
    queryFn: async () => (await api.get<Metrics>("/metrics", { params: { source } })).data,
    retry: false,
  });
}

export function useImportance(source = "kalboard") {
  return useQuery({
    queryKey: ["importance", source],
    queryFn: async () => (await api.get<Importance>("/importance", { params: { source } })).data,
    retry: false,
  });
}

export function usePredict(source = "kalboard") {
  return useMutation({
    mutationFn: async (payload: PredictionRequest) =>
      (await api.post<PredictionResponse>("/predict", payload, { params: { source } })).data,
  });
}

export function useOptions() {
  return useQuery({
    queryKey: ["options"],
    queryFn: async () => (await api.get<LearnerOptions>("/options")).data,
  });
}

export function useLearners(params: {
  limit: number;
  offset: number;
  topic?: string;
  tier?: string;
}) {
  return useQuery({
    queryKey: ["learners", params],
    queryFn: async () => (await api.get<LearnerPage>("/learners", { params })).data,
  });
}

export function useResults() {
  return useQuery({
    queryKey: ["results"],
    queryFn: async () => (await api.get<ResultsPayload>("/results")).data,
  });
}

export function useDiagnostics(source = "kalboard") {
  return useQuery({
    queryKey: ["diagnostics", source],
    queryFn: async () =>
      (await api.get<DiagnosticsPayload>("/model/diagnostics", { params: { source } })).data,
    retry: false,
  });
}

export function useModelFeatures(source = "kalboard") {
  return useQuery({
    queryKey: ["model-features", source],
    queryFn: async () =>
      (await api.get<ModelFeatures>("/model/features", { params: { source } })).data,
    retry: false,
  });
}

export function useColumns() {
  return useQuery({
    queryKey: ["columns"],
    queryFn: async () => (await api.get<ColumnsPayload>("/analytics/columns")).data,
  });
}

export function useAnalyticsQuery(spec: Record<string, unknown>, enabled = true) {
  return useQuery({
    queryKey: ["analytics-query", spec],
    queryFn: async () => (await api.post<AnalyticsQueryResult>("/analytics/query", spec)).data,
    enabled,
  });
}

export function useChartViews() {
  return useQuery({
    queryKey: ["chart-views"],
    queryFn: async () => (await api.get<SavedChartView[]>("/charts")).data,
  });
}

export function useSaveChartView() {
  return useMutation({
    mutationFn: async (view: { name: string; spec: Record<string, unknown> }) =>
      (await api.post<SavedChartView>("/charts", view)).data,
  });
}

export function useDeleteChartView() {
  return useMutation({
    mutationFn: async (name: string) =>
      (await api.delete(`/charts/${encodeURIComponent(name)}`)).data,
  });
}

export function useCorrelation() {
  return useQuery({
    queryKey: ["correlation"],
    queryFn: async () => (await api.get<CorrelationPayload>("/analytics/correlation")).data,
  });
}

export function useEmbedding(clusters = 3) {
  return useQuery({
    queryKey: ["embedding", clusters],
    queryFn: async () =>
      (await api.get<EmbeddingPayload>("/analytics/embedding", { params: { clusters } })).data,
  });
}

export function usePdp(feature: string, enabled = true) {
  return useQuery({
    queryKey: ["pdp", feature],
    queryFn: async () => (await api.get<PdpPayload>("/model/pdp", { params: { feature } })).data,
    enabled: enabled && Boolean(feature),
    retry: false,
  });
}

export function useXrPilots() {
  return useQuery({
    queryKey: ["xr-pilots"],
    queryFn: async () => (await api.get<XrPilotsPayload>("/xr/pilots")).data,
  });
}
export function useXrTrends(pilot = "pbis", freq = "W", enabled = true) {
  return useQuery({
    queryKey: ["xr-trends", pilot, freq],
    queryFn: async () => (await api.get<XrTrends>("/xr/trends", { params: { pilot, freq } })).data,
    enabled,
    retry: false,
  });
}

export function useXrRisk(pilot = "pbis", folds = 5, enabled = true) {
  return useQuery({
    queryKey: ["xr-risk", pilot, folds],
    queryFn: async () => (await api.get<XrRisk>("/xr/risk", { params: { pilot, folds } })).data,
    enabled,
    retry: false,
  });
}
export function useXrLearners(pilot = "pbis", limit = 50, offset = 0, enabled = true) {
  return useQuery({
    queryKey: ["xr-learners", pilot, limit, offset],
    queryFn: async () =>
      (
        await api.get<XrLearnerPage>("/xr/learners", {
          params: { pilot, limit, offset },
        })
      ).data,
    enabled,
    retry: false,
  });
}

export function useEvaluation() {
  return useQuery({
    queryKey: ["evaluation"],
    queryFn: async () => (await api.get<EvaluationPayload>("/evaluation")).data,
    retry: false,
  });
}

export function useDatasets() {
  return useQuery({
    queryKey: ["datasets"],
    queryFn: async () => (await api.get<DatasetList>("/datasets")).data,
    retry: false,
  });
}

export function useUploadDataset() {
  return useMutation({
    mutationFn: async (input: {
      name: string;
      description: string;
      target: string;
      classLabels: string;
      file: File;
    }) => {
      const form = new FormData();
      form.append("name", input.name);
      form.append("description", input.description);
      form.append("target", input.target);
      form.append("class_labels", input.classLabels);
      form.append("file", input.file);
      return (await api.post("/datasets", form)).data;
    },
  });
}

export function useDeleteDataset() {
  return useMutation({
    mutationFn: async (name: string) => (await api.delete(`/datasets/${name}`)).data,
  });
}

export function useTrainDataset() {
  return useMutation({
    mutationFn: async (input: { name: string; mode: string; model?: string }) =>
      (
        await api.post(`/datasets/${input.name}/train`, null, {
          params: { mode: input.mode, ...(input.model ? { model: input.model } : {}) },
        })
      ).data,
  });
}
