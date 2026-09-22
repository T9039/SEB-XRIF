import { BarChart } from "../charts/Chart";
import { useTrends } from "../api/hooks";

const BEHAVIOURS = ["raisedhands", "VisITedResources", "AnnouncementsView", "Discussion"];

export function TrendChart() {
  const { data, isLoading, isError } = useTrends();

  if (isLoading) return <p className="muted">Loading behavioural trends…</p>;
  if (isError || !data) return <p className="muted">Trends unavailable.</p>;

  const tiers = Object.keys(data.behaviour_by_class);

  return (
    <div className="panel">
      <h3>Mean behaviour by tier</h3>
      <BarChart
        data={{
          labels: BEHAVIOURS,
          datasets: tiers.map((tier, index) => ({
            label: tier,
            data: BEHAVIOURS.map((b) => data.behaviour_by_class[tier][b] ?? 0),
            backgroundColor: ["#4472C4", "#ED7D31", "#70AD47"][index % 3],
          })),
        }}
        options={{
          responsive: true,
          plugins: { legend: { position: "bottom" } },
          scales: { y: { beginAtZero: true } },
        }}
      />
    </div>
  );
}
