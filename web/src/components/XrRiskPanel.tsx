import { Bar, BarChart, CartesianGrid, XAxis, YAxis } from "recharts";
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
import { useXrRisk } from "../api/hooks";
import { useSource } from "../lib/source-context";

const bandConfig = {
  count: { label: "Learners", color: "#C00000" },
} satisfies ChartConfig;

const featureConfig = {
  importance: { label: "Importance", color: "#4472C4" },
} satisfies ChartConfig;

function metric(value: number | undefined): string {
  return value === undefined ? "—" : value.toFixed(3);
}

/** Early-warning engagement/risk bands over the selected ARETE pilot. */
export function XrRiskPanel() {
  const { source, sourceId } = useSource();
  const isXr = source.kind === "xr";
  const { data, isLoading, isError } = useXrRisk(sourceId, 5, isXr);

  const bands = Object.entries(data?.bands ?? {}).map(([band, count]) => ({ band, count }));
  const importances = Object.entries(data?.importances ?? {}).map(([feature, importance]) => ({
    feature,
    importance,
  }));

  return (
    <Card>
      <CardHeader>
        <CardTitle>XR early-warning risk{isXr ? ` (${sourceId})` : ""}</CardTitle>
        <CardDescription>
          Predicts later engagement from early-session behaviour · {data?.n ?? 0} learners,{" "}
          {data?.positives ?? 0} flagged outcomes
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
          <Skeleton className="h-56 w-full" />
        ) : isError || !data ? (
          <Alert>
            <AlertDescription>
              Download this pilot with `make fetch-arete ARGS={sourceId}`.
            </AlertDescription>
          </Alert>
        ) : !data.available ? (
          <Alert>
            <AlertDescription>{data.reason ?? "No usable cohort for this pilot."}</AlertDescription>
          </Alert>
        ) : (
          <>
            <div className="grid grid-cols-3 gap-3 text-sm">
              <div>
                <div className="text-muted-foreground">ROC-AUC</div>
                <div className="font-heading text-xl">{metric(data.roc_auc)}</div>
              </div>
              <div>
                <div className="text-muted-foreground">Avg precision</div>
                <div className="font-heading text-xl">{metric(data.average_precision)}</div>
              </div>
              <div>
                <div className="text-muted-foreground">Brier</div>
                <div className="font-heading text-xl">{metric(data.brier)}</div>
              </div>
            </div>
            <ChartContainer config={bandConfig} className="h-48 w-full">
              <BarChart data={bands}>
                <CartesianGrid vertical={false} />
                <XAxis dataKey="band" tickLine={false} axisLine={false} tickMargin={8} />
                <YAxis tickLine={false} axisLine={false} tickMargin={8} allowDecimals={false} />
                <ChartTooltip content={<ChartTooltipContent />} />
                <Bar dataKey="count" fill="var(--color-count)" radius={4} />
              </BarChart>
            </ChartContainer>
            <ChartContainer config={featureConfig} className="h-56 w-full">
              <BarChart data={importances} layout="vertical">
                <CartesianGrid horizontal={false} />
                <XAxis type="number" tickLine={false} axisLine={false} tickMargin={8} />
                <YAxis
                  type="category"
                  dataKey="feature"
                  width={140}
                  tickLine={false}
                  axisLine={false}
                  tickMargin={8}
                />
                <ChartTooltip content={<ChartTooltipContent />} />
                <Bar dataKey="importance" fill="var(--color-importance)" radius={4} />
              </BarChart>
            </ChartContainer>
          </>
        )}
      </CardContent>
    </Card>
  );
}
