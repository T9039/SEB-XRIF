import { Cell, Pie, PieChart } from "recharts";
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
import { useTrends } from "../api/hooks";
import { PanelMessage, PanelSkeleton } from "./panel-states";

const COLOURS = ["#4472C4", "#ED7D31", "#70AD47"];

const config = {
  count: { label: "Learners" },
} satisfies ChartConfig;

export function TierDistribution() {
  const { data, isLoading, isError } = useTrends();

  if (isLoading) return <PanelSkeleton title="Performance tiers" />;
  if (isError || !data) {
    return <PanelMessage title="Performance tiers" message="Trends unavailable." />;
  }

  const chartData = Object.entries(data.class_counts).map(([tier, count]) => ({
    tier,
    count,
  }));

  return (
    <Card>
      <CardHeader>
        <CardTitle>Performance tiers</CardTitle>
      </CardHeader>
      <CardContent>
        <ChartContainer config={config} className="mx-auto aspect-square max-h-64">
          <PieChart>
            <ChartTooltip content={<ChartTooltipContent nameKey="tier" />} />
            <Pie data={chartData} dataKey="count" nameKey="tier" innerRadius={55} outerRadius={90}>
              {chartData.map((entry, index) => (
                <Cell key={entry.tier} fill={COLOURS[index % COLOURS.length]} />
              ))}
            </Pie>
          </PieChart>
        </ChartContainer>
      </CardContent>
    </Card>
  );
}
