import { Bar, BarChart, XAxis, YAxis } from "recharts";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from "@humanity-erp/ui";
import { useImportance } from "../api/hooks";
import { useSource } from "../lib/source-context";
import { PanelMessage, PanelSkeleton } from "./panel-states";

const config = {
  value: { label: "Importance", color: "#4472C4" },
} satisfies ChartConfig;

export function ImportancePanel() {
  const { sourceId } = useSource();
  const { data, isLoading, isError } = useImportance(sourceId);

  if (isLoading) return <PanelSkeleton title="Top behavioural drivers" />;
  if (isError || !data) {
    return (
      <PanelMessage
        title="Top behavioural drivers"
        message="No importance payload — train a model first."
      />
    );
  }

  const scores =
    data.shap?.available && data.shap.mean_abs_shap
      ? data.shap.mean_abs_shap
      : (data.native?.importance ?? {});

  const entries = Object.entries(scores)
    .slice(0, 10)
    .map(([name, value]) => ({ feature: name.replace(/^(cat|num)__/, ""), value }));

  if (entries.length === 0) {
    return <PanelMessage title="Top behavioural drivers" message="Importance payload is empty." />;
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Top behavioural drivers</CardTitle>
      </CardHeader>
      <CardContent>
        <ChartContainer config={config} className="h-72 w-full">
          <BarChart data={entries} layout="vertical" margin={{ left: 8, right: 8 }}>
            <XAxis type="number" hide />
            <YAxis
              type="category"
              dataKey="feature"
              tickLine={false}
              axisLine={false}
              width={150}
            />
            <ChartTooltip content={<ChartTooltipContent />} />
            <Bar dataKey="value" fill="var(--color-value)" radius={4} />
          </BarChart>
        </ChartContainer>
      </CardContent>
    </Card>
  );
}
