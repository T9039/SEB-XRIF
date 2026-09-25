import { Bar, BarChart, CartesianGrid, ComposedChart, Line, XAxis, YAxis } from "recharts";
import {
  Alert,
  AlertDescription,
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  Skeleton,
  type ChartConfig,
} from "@humanity-erp/ui";
import { useXrTrends } from "../api/hooks";
import { useSource } from "../lib/source-context";

const timelineConfig = {
  events: { label: "Events", color: "#4472C4" },
  active_learners: { label: "Active learners", color: "#ED7D31" },
} satisfies ChartConfig;

const verbConfig = {
  count: { label: "Events", color: "#70AD47" },
} satisfies ChartConfig;

/** Engagement trends over the selected ARETE augmented-reality pilot. */
export function XrTrendsPanel() {
  const { source, sourceId } = useSource();
  const isXr = source.kind === "xr";
  const { data, isLoading, isError } = useXrTrends(sourceId, "W", isXr);

  const timeline = (data?.period_start ?? []).map((period, index) => ({
    period: period.slice(0, 10),
    events: data?.events_by_period[index] ?? 0,
    active_learners: data?.active_learners_by_period[index] ?? 0,
  }));
  const verbs = Object.entries(data?.verb_counts ?? {}).map(([verb, count]) => ({
    verb,
    count,
  }));

  return (
    <Card>
      <CardHeader>
        <CardTitle>XR engagement over time{isXr ? ` (${sourceId})` : ""}</CardTitle>
        <CardDescription>
          {isXr
            ? `${source.description} · ${data?.learners ?? 0} learners, ${data?.events ?? 0} xAPI statements`
            : "Select an ARETE XR pilot in the header to see engagement trends."}
        </CardDescription>
      </CardHeader>
      <CardContent className="flex flex-col gap-6">
        {!isXr ? (
          <Alert>
            <AlertDescription>
              The active source is LMS data. Choose an ARETE pilot in the header.
            </AlertDescription>
          </Alert>
        ) : isLoading ? (
          <Skeleton className="h-72 w-full" />
        ) : isError || !data ? (
          <Alert>
            <AlertDescription>
              Download this pilot with `make fetch-arete ARGS={sourceId}`.
            </AlertDescription>
          </Alert>
        ) : (
          <>
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
          </>
        )}
      </CardContent>
    </Card>
  );
}
