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

const SUPPORT_BANDS: Record<string, string> = {
  L: "priority-support",
  M: "monitor",
  H: "on-track",
};

const config = {
  count: { label: "Learners" },
} satisfies ChartConfig;

export function TierDistribution() {
  const { data, isLoading, isError } = useTrends();

  if (isLoading) return <PanelSkeleton title="Support bands" />;
  if (isError || !data) {
    return <PanelMessage title="Support bands" message="Trends unavailable." />;
  }

  const chartData = Object.entries(data.class_counts).map(([tier, count]) => ({
    tier,
    band: SUPPORT_BANDS[tier] ?? tier,
    count,
  }));

  return (
    <Card>
      <CardHeader>
        <CardTitle>Support bands</CardTitle>
      </CardHeader>
      <CardContent>
        <ChartContainer config={config} className="mx-auto aspect-square max-h-64">
          <PieChart>
            <ChartTooltip content={<ChartTooltipContent nameKey="band" />} />
            <Pie data={chartData} dataKey="count" nameKey="band" innerRadius={55} outerRadius={90}>
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
