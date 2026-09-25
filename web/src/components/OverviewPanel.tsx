import { useSource } from "../lib/source-context";
import { EvaluationPanel } from "./EvaluationPanel";
import { MetricCards } from "./MetricCards";
import { TierDistribution } from "./TierDistribution";
import { TrendChart } from "./TrendChart";
import { XrOverview } from "./XrOverview";

/** The Overview tab follows the active data source. */
export function OverviewPanel() {
  const { source } = useSource();

  if (source.kind === "xr") {
    return (
      <div className="flex flex-col gap-4">
        <XrOverview />
        <EvaluationPanel />
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-4">
      <MetricCards />
      <div className="grid gap-4 lg:grid-cols-2">
        <TierDistribution />
        <TrendChart />
      </div>
      <EvaluationPanel />
    </div>
  );
}
