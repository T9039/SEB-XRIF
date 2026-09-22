import { DoughnutChart } from "../charts/Chart";
import { useTrends } from "../api/hooks";

const COLOURS = ["#4472C4", "#ED7D31", "#70AD47"];

export function TierDistribution() {
  const { data, isLoading, isError } = useTrends();

  if (isLoading) return <p className="muted">Loading distribution…</p>;
  if (isError || !data) return <p className="muted">Trends unavailable.</p>;

  const labels = Object.keys(data.class_counts);
  const values = labels.map((label) => data.class_counts[label]);

  return (
    <div className="panel">
      <h3>Performance tiers</h3>
      <DoughnutChart
        data={{
          labels,
          datasets: [
            {
              data: values,
              backgroundColor: COLOURS.slice(0, labels.length),
            },
          ],
        }}
        options={{ plugins: { legend: { position: "bottom" } } }}
      />
    </div>
  );
}
