import { useMutation, useQuery } from "@tanstack/react-query";
import { api } from "./client";
import type {
  Health,
  Importance,
  Metrics,
  PredictionRequest,
  PredictionResponse,
  Trends,
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

export function useMetrics() {
  return useQuery({
    queryKey: ["metrics"],
    queryFn: async () => (await api.get<Metrics>("/metrics")).data,
  });
}

export function useImportance() {
  return useQuery({
    queryKey: ["importance"],
    queryFn: async () => (await api.get<Importance>("/importance")).data,
  });
}

export function usePredict() {
  return useMutation({
    mutationFn: async (payload: PredictionRequest) =>
      (await api.post<PredictionResponse>("/predict", payload)).data,
  });
}
