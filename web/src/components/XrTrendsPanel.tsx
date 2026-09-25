import { Bar, BarChart, CartesianGrid, ComposedChart, Line, XAxis, YAxis } from "recharts";
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
import { useXrTrends } from "../api/hooks";
import { PanelMessage, PanelSkeleton } from "./panel-states";

const timelineConfig = {
  events: { label: "Events", color: "#4472C4" },
  active_learners: { label: "Active learners", color: "#ED7D31" },
} satisfies ChartConfig;

const verbConfig = {
  count: { label: "Events", color: "#70AD47" },
} satisfies ChartConfig;

/** Engagement trends over the ARETE PBIS augmented-reality pilot. */
export function XrTrendsPanel() {
  const { data, isLoading, isError } = useXrTrends("pbis", "W");

  if (isLoading) return <PanelSkeleton title="XR engagement over time" />;
  if (isError || !data) {
    return (
      <PanelMessage
        title="XR engagement over time"
        message="Download the PBIS pilot with `make fetch-arete`."
      />
    );
  }

  const timeline = data.period_start.map((period, index) => ({
    period: period.slice(0, 10),
    events: data.events_by_period[index],
    active_learners: data.active_learners_by_period[index],
  }));
  const verbs = Object.entries(data.verb_counts).map(([verb, count]) => ({ verb, count }));

  return (
    <Card>
      <CardHeader>
        <CardTitle>XR engagement over time ({data.pilot})</CardTitle>
        <CardDescription>
          {data.learners} learners, {data.events} xAPI statements across the pilot · licence{" "}
          {data.licence}
        </CardDescription>
      </CardHeader>
      <CardContent className="flex flex-col gap-6">
        <ChartContainer config={timelineConfig} className="h-72 w-full">
          <ComposedChart data={timeline}>
            <CartesianGrid vertical={false} />
            <XAxis dataKey="period" tickLine={false} axisLine={false} tickMargin={8} />
            <YAxis tickLine={false} axisLine={false} tickMargin={8} />
            <ChartTooltip content={<ChartTooltipContent />} />
            <Bar dataKey="events" fill="var(--color-events)" radius={4} />
            <Line
              dataKey="active_learners"
              stroke="var(--color-active_learners)"
              strokeWidth={2}
              dot={false}
            />
          </ComposedChart>
        </ChartContainer>
        <ChartContainer config={verbConfig} className="h-56 w-full">
          <BarChart data={verbs}>
            <CartesianGrid vertical={false} />
            <XAxis dataKey="verb" tickLine={false} axisLine={false} tickMargin={8} />
            <YAxis tickLine={false} axisLine={false} tickMargin={8} />
            <ChartTooltip content={<ChartTooltipContent />} />
            <Bar dataKey="count" fill="var(--color-count)" radius={4} />
          </BarChart>
        </ChartContainer>
      </CardContent>
    </Card>
  );
}
