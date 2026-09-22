import { useHealth } from "../api/hooks";

export function HealthBadge() {
  const { data, isLoading, isError } = useHealth();

  const label = isLoading
    ? "checking..."
    : isError
      ? "api unreachable"
      : data?.model_loaded
        ? `model: ${data.model_version}`
        : "no model trained";

  const tone = isLoading
    ? "neutral"
    : isError
      ? "error"
      : data?.model_loaded
        ? "ok"
        : "warn";

  return <span className={`badge badge-${tone}`}>{label}</span>;
}
