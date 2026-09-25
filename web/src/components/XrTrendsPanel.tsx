import { useState } from "react";
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
  Label,
  NativeSelect,
  NativeSelectOption,
  Skeleton,
  type ChartConfig,
} from "@humanity-erp/ui";
import { useXrPilots, useXrTrends } from "../api/hooks";

const timelineConfig = {
  events: { label: "Events", color: "#4472C4" },
  active_learners: { label: "Active learners", color: "#ED7D31" },
} satisfies ChartConfig;

const verbConfig = {
  count: { label: "Events", color: "#70AD47" },
} satisfies ChartConfig;

/** Engagement trends over the ARETE augmented-reality pilots. */
export function XrTrendsPanel() {
  const pilots = useXrPilots();
  const [pilot, setPilot] = useState("pbis");
  const { data, isLoading, isError } = useXrTrends(pilot, "W");

  const options = pilots.data?.pilots ?? [];
  const selected = options.find((option) => option.name === pilot);

  const timeline = (data?.period_start ?? []).map((period, index) => ({
    period: period.slice(0, 10),
    events: data?.events_by_period[index] ?? 0,
    active_learners: data?.active_learners_by_period[index] ?? 0,
  }));
  const verbs = Object.entries(data?.verb_counts ?? {}).map(([verb, count]) => ({
    verb,
    count,
  }));

  const description = data
    ? `${selected?.description ?? ""} · ${data.learners} learners, ${data.events} xAPI statements · licence ${data.licence}`
    : "Select an ARETE pilot. Download it with `make fetch-arete` if the chart is empty.";

  return (
    <Card>
      <CardHeader>
        <CardTitle>XR engagement over time{pilot ? ` (${pilot})` : ""}</CardTitle>
        <CardDescription>{description}</CardDescription>
      </CardHeader>
      <CardContent className="flex flex-col gap-6">
        <div className="flex flex-col gap-1">
          <Label htmlFor="xr-pilot">XR pilot</Label>
          <NativeSelect
            id="xr-pilot"
            value={pilot}
            onChange={(event) => setPilot(event.target.value)}
            disabled={options.length === 0}
          >
            {options.map((option) => (
              <NativeSelectOption key={option.name} value={option.name}>
                {option.name}
                {option.available ? "" : " (not downloaded)"}
              </NativeSelectOption>
            ))}
          </NativeSelect>
        </div>

        {isLoading ? (
          <Skeleton className="h-72 w-full" />
        ) : isError || !data ? (
          <Alert>
            <AlertDescription>
              Download this pilot with `make fetch-arete ARGS={pilot}`.
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
