import { Bar, BarChart, CartesianGrid, XAxis, YAxis } from "recharts";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  ChartContainer,
  ChartLegend,
  ChartLegendContent,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from "@humanity-erp/ui";
import { useTrends } from "../api/hooks";
import { PanelMessage, PanelSkeleton } from "./panel-states";

const BEHAVIOURS = ["raisedhands", "VisITedResources", "AnnouncementsView", "Discussion"];
const COLOURS = ["#4472C4", "#ED7D31", "#70AD47"];

export function TrendChart() {
  const { data, isLoading, isError } = useTrends();

  if (isLoading) return <PanelSkeleton title="Mean behaviour by tier" />;
  if (isError || !data) {
    return <PanelMessage title="Mean behaviour by tier" message="Trends unavailable." />;
  }

  const tiers = Object.keys(data.behaviour_by_class);
  const chartData = BEHAVIOURS.map((behaviour) => {
    const row: Record<string, string | number> = { behaviour };
    for (const tier of tiers) {
      row[tier] = data.behaviour_by_class[tier][behaviour] ?? 0;
    }
    return row;
  });

  const config = Object.fromEntries(
    tiers.map((tier, index) => [tier, { label: tier, color: COLOURS[index % COLOURS.length] }]),
  ) satisfies ChartConfig;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Mean behaviour by tier</CardTitle>
      </CardHeader>
      <CardContent>
        <ChartContainer config={config} className="h-72 w-full">
          <BarChart data={chartData}>
            <CartesianGrid vertical={false} />
            <XAxis dataKey="behaviour" tickLine={false} axisLine={false} tickMargin={8} />
            <YAxis tickLine={false} axisLine={false} tickMargin={8} />
            <ChartTooltip content={<ChartTooltipContent />} />
            <ChartLegend content={<ChartLegendContent />} />
            {tiers.map((tier) => (
              <Bar key={tier} dataKey={tier} fill={`var(--color-${tier})`} radius={4} />
            ))}
          </BarChart>
        </ChartContainer>
      </CardContent>
    </Card>
  );
}
