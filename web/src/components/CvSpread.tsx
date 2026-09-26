import { Bar, BarChart, XAxis, YAxis } from "recharts";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from "@humanity-erp/ui";
import { useMetrics } from "../api/hooks";
import { useSource } from "../lib/source-context";
import { PanelMessage, PanelSkeleton } from "./panel-states";

const config = {
  score: { label: "Macro F1", color: "#4472C4" },
} satisfies ChartConfig;

interface CvPayload {
  scores?: number[];
  mean?: number;
  std?: number;
}

export function CvSpread() {
  const { sourceId } = useSource();
  const { data, isLoading, isError } = useMetrics(sourceId);

  if (isLoading) return <PanelSkeleton title="Cross-validation spread" />;
  if (isError || !data) {
    return (
      <PanelMessage
        title="Cross-validation spread"
        message="No metrics yet — train a model first."
      />
    );
  }

  const cv = data.metrics.cv as CvPayload | undefined;
  const scores = cv?.scores ?? [];

  if (scores.length === 0) {
    return (
      <PanelMessage
        title="Cross-validation spread"
        message="No cross-validation scores in the model metadata."
      />
    );
  }

  const chartData = scores.map((score, index) => ({ fold: `F${index + 1}`, score }));

  return (
    <Card>
      <CardHeader>
        <CardTitle>Cross-validation spread</CardTitle>
        <CardDescription>
          {scores.length} folds · mean {((cv?.mean ?? 0) * 100).toFixed(1)}% ±{" "}
          {((cv?.std ?? 0) * 100).toFixed(1)}%
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ChartContainer config={config} className="h-56 w-full">
          <BarChart data={chartData}>
            <XAxis dataKey="fold" tickLine={false} axisLine={false} />
            <YAxis domain={[0, 1]} tickLine={false} axisLine={false} />
            <ChartTooltip content={<ChartTooltipContent />} />
            <Bar dataKey="score" fill="var(--color-score)" radius={4} />
          </BarChart>
        </ChartContainer>
      </CardContent>
    </Card>
  );
}
