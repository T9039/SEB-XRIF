import { BarChart } from "../charts/Chart";
import { useImportance } from "../api/hooks";

export function ImportancePanel() {
  const { data, isLoading, isError } = useImportance();

  if (isLoading) return <p className="muted">Loading feature importance…</p>;
  if (isError || !data) {
    return <p className="muted">No importance payload — train a model first.</p>;
  }

  const scores =
    data.shap?.available && data.shap.mean_abs_shap
      ? data.shap.mean_abs_shap
      : (data.native?.importance ?? {});

  const entries = Object.entries(scores).slice(0, 10);

  if (entries.length === 0) {
    return <p className="muted">Importance payload is empty.</p>;
  }

  return (
    <div className="panel">
      <h3>Top behavioural drivers</h3>
      <BarChart
        data={{
          labels: entries.map(([name]) => name.replace(/^(cat|num)__/, "")),
          datasets: [{ label: "importance", data: entries.map(([, v]) => v) }],
        }}
        options={{
          indexAxis: "y" as const,
          plugins: { legend: { display: false } },
          scales: { x: { beginAtZero: true } },
        }}
      />
    </div>
  );
}
