import { Card, CardContent, CardHeader, CardTitle } from "@humanity-erp/ui";
import { useXrRisk, useXrTrends } from "../api/hooks";
import { useSource } from "../lib/source-context";
import { PanelSkeleton } from "./panel-states";
import { XrTrendsPanel } from "./XrTrendsPanel";

function Stat({ label, value }: { label: string; value: string | number }) {
  return (
    <div>
      <div className="text-xs tracking-wide text-muted-foreground uppercase">{label}</div>
      <div className="font-heading text-lg">{value}</div>
    </div>
  );
}

/** XR engagement summary for the selected pilot. */
export function XrOverview() {
  const { sourceId } = useSource();
  const trends = useXrTrends(sourceId, "W", true);
  const risk = useXrRisk(sourceId, 5, true);

  if (trends.isLoading) return <PanelSkeleton title="XR overview" />;
  const data = trends.data;
  const elevated = risk.data?.bands?.elevated;

  return (
    <div className="flex flex-col gap-4">
      <Card>
        <CardHeader>
          <CardTitle>XR overview ({sourceId})</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          <Stat label="Learners" value={data?.learners ?? 0} />
          <Stat label="xAPI statements" value={data?.events ?? 0} />
          <Stat label="First seen" value={data?.first_seen?.slice(0, 10) ?? "—"} />
          <Stat label="Elevated risk learners" value={elevated ?? "—"} />
        </CardContent>
      </Card>
      <XrTrendsPanel />
    </div>
  );
}
