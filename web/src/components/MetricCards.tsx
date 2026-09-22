import { useMetrics } from "../api/hooks";

function format(value: unknown): string {
  if (typeof value === "number") {
    return value <= 1 ? `${(value * 100).toFixed(1)}%` : value.toFixed(2);
  }
  return "—";
}

export function MetricCards() {
  const { data, isLoading, isError } = useMetrics();

  if (isLoading) return <p className="muted">Loading metrics…</p>;
  if (isError || !data) {
    return <p className="muted">No metrics yet — train a model to populate this panel.</p>;
  }

  const metrics = data.metrics as Record<string, unknown>;
  const cv = metrics.cv as { mean?: number; std?: number } | undefined;

  const cards = [
    { label: "Accuracy", value: format(metrics.accuracy) },
    { label: "Macro F1", value: format(metrics.f1_macro) },
    { label: "CV macro F1", value: format(cv?.mean) },
    { label: "Model", value: String(data.model ?? "—") },
  ];

  return (
    <div className="cards">
      {cards.map((card) => (
        <div className="card" key={card.label}>
          <span className="card-label">{card.label}</span>
          <span className="card-value">{card.value}</span>
        </div>
      ))}
    </div>
  );
}
