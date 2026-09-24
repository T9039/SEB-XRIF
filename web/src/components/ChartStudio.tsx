import { useMemo, useRef, useState } from "react";
import {
  Button,
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  Input,
  Label,
  NativeSelect,
  NativeSelectOption,
  Separator,
} from "@humanity-erp/ui";
import {
  useAnalyticsQuery,
  useChartViews,
  useColumns,
  useDeleteChartView,
  useResults,
  useSaveChartView,
} from "../api/hooks";
import { ChartRenderer, type ChartSpec, type ChartType } from "../charts/ChartRenderer";
import { chartConfig } from "../charts/color";
import type { Row } from "../charts/data";
import { buildChartSpec, type StudioConfig } from "../charts/spec";
import { downloadCsv, downloadJson, downloadPng, downloadSvg } from "../lib/export";

const CHART_TYPES: { value: ChartType; label: string }[] = [
  { value: "bar", label: "Bar (stacked when grouped)" },
  { value: "line", label: "Line" },
  { value: "area", label: "Area" },
  { value: "composed", label: "Composed (bar + line)" },
  { value: "radar", label: "Radar" },
  { value: "pie", label: "Pie / donut" },
  { value: "treemap", label: "Treemap" },
  { value: "funnel", label: "Funnel" },
  { value: "radial", label: "Radial" },
];

const AGGREGATES = ["mean", "median", "sum", "min", "max", "count"];
const RESULTS_METRICS = ["cv_mean", "accuracy", "f1_macro", "roc_auc_ovr", "fit_seconds"];

export function ChartStudio() {
  const [source, setSource] = useState<"learners" | "results">("learners");
  const [type, setType] = useState<ChartType>("bar");
  const [x, setX] = useState("Topic");
  const [y, setY] = useState("raisedhands");
  const [group, setGroup] = useState("");
  const [aggregate, setAggregate] = useState("mean");
  const [filterTopic, setFilterTopic] = useState("");
  const [filterTier, setFilterTier] = useState("");
  const [sort, setSort] = useState("x");
  const [resultsMetric, setResultsMetric] = useState("cv_mean");
  const [savedName, setSavedName] = useState("");
  const previewRef = useRef<HTMLDivElement>(null);

  const { data: columns } = useColumns();
  const categorical = (columns?.columns ?? []).filter(
    (column) => column.kind === "categorical" && column.name !== "Class",
  );
  const numeric = (columns?.columns ?? []).filter((column) => column.kind === "numeric");

  const filters = useMemo(
    () => ({
      ...(filterTopic ? { Topic: filterTopic } : {}),
      ...(filterTier ? { Class: filterTier } : {}),
    }),
    [filterTopic, filterTier],
  );

  const querySpec = { x, y: y || null, group: group || null, aggregate, filters, sort, limit: 30 };
  const query = useAnalyticsQuery(querySpec, source === "learners");
  const results = useResults();

  const resultsRows: Row[] = useMemo(
    () =>
      (results.data?.results ?? []).map((row) => ({
        x: row.model,
        value: Number((row as unknown as Record<string, number>)[resultsMetric] ?? 0),
      })),
    [results.data, resultsMetric],
  );

  const spec: ChartSpec = useMemo(() => {
    if (source === "results") {
      return {
        type: type === "line" ? "line" : "bar",
        rows: resultsRows,
        series: ["value"],
        xKey: "x",
        config: chartConfig(["value"], { value: resultsMetric }),
        showLegend: false,
      };
    }
    const config: StudioConfig = { type, x, y, group, aggregate, source };
    return buildChartSpec(config, (query.data?.rows ?? []) as Row[], query.data?.series ?? []);
  }, [source, type, x, y, group, aggregate, query.data, resultsRows, resultsMetric]);

  const views = useChartViews();
  const saveView = useSaveChartView();
  const deleteView = useDeleteChartView();

  const currentRows = source === "learners" ? ((query.data?.rows ?? []) as Row[]) : resultsRows;
  const busy = source === "learners" ? query.isLoading : results.isLoading;
  const error = source === "learners" ? query.error : results.error;

  const getSvg = () => previewRef.current?.querySelector("svg") as SVGSVGElement | null;

  const handleSave = async () => {
    if (!savedName.trim()) return;
    await saveView.mutateAsync({
      name: savedName.trim(),
      spec: { source, type, x, y, group, aggregate, sort, resultsMetric },
    });
    setSavedName("");
    views.refetch();
  };

  const handleLoad = (view: { spec: Record<string, unknown> }) => {
    const saved = view.spec as Partial<{
      source: "learners" | "results";
      type: ChartType;
      x: string;
      y: string;
      group: string;
      aggregate: string;
      sort: string;
      resultsMetric: string;
    }>;
    if (saved.source) setSource(saved.source);
    if (saved.type) setType(saved.type);
    if (saved.x) setX(saved.x);
    if (saved.y !== undefined) setY(saved.y);
    if (saved.group !== undefined) setGroup(saved.group);
    if (saved.aggregate) setAggregate(saved.aggregate);
    if (saved.sort) setSort(saved.sort);
    if (saved.resultsMetric) setResultsMetric(saved.resultsMetric);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Chart Studio</CardTitle>
        <CardDescription>
          Pick a source, metric, and chart type, then export or save the view.
        </CardDescription>
      </CardHeader>
      <CardContent className="flex flex-col gap-5">
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <div className="flex flex-col gap-1">
            <Label htmlFor="studio-source">Source</Label>
            <NativeSelect
              id="studio-source"
              className="w-full"
              value={source}
              onChange={(event) => setSource(event.target.value as "learners" | "results")}
            >
              <NativeSelectOption value="learners">Learners</NativeSelectOption>
              <NativeSelectOption value="results">Model results (16 models)</NativeSelectOption>
            </NativeSelect>
          </div>

          <div className="flex flex-col gap-1">
            <Label htmlFor="studio-type">Chart type</Label>
            <NativeSelect
              id="studio-type"
              className="w-full"
              value={type}
              onChange={(event) => setType(event.target.value as ChartType)}
            >
              {CHART_TYPES.map((option) => (
                <NativeSelectOption key={option.value} value={option.value}>
                  {option.label}
                </NativeSelectOption>
              ))}
            </NativeSelect>
          </div>

          {source === "learners" ? (
            <>
              <div className="flex flex-col gap-1">
                <Label htmlFor="studio-x">Dimension (x)</Label>
                <NativeSelect
                  id="studio-x"
                  className="w-full"
                  value={x}
                  onChange={(event) => setX(event.target.value)}
                >
                  {categorical.map((column) => (
                    <NativeSelectOption key={column.name} value={column.name}>
                      {column.name}
                    </NativeSelectOption>
                  ))}
                </NativeSelect>
              </div>
              <div className="flex flex-col gap-1">
                <Label htmlFor="studio-y">Metric (y)</Label>
                <NativeSelect
                  id="studio-y"
                  className="w-full"
                  value={y}
                  onChange={(event) => setY(event.target.value)}
                >
                  <NativeSelectOption value="">count</NativeSelectOption>
                  {numeric.map((column) => (
                    <NativeSelectOption key={column.name} value={column.name}>
                      {column.name}
                    </NativeSelectOption>
                  ))}
                </NativeSelect>
              </div>
              <div className="flex flex-col gap-1">
                <Label htmlFor="studio-group">Group / series</Label>
                <NativeSelect
                  id="studio-group"
                  className="w-full"
                  value={group}
                  onChange={(event) => setGroup(event.target.value)}
                >
                  <NativeSelectOption value="">none</NativeSelectOption>
                  <NativeSelectOption value="Class">Class</NativeSelectOption>
                  {categorical.map((column) => (
                    <NativeSelectOption key={column.name} value={column.name}>
                      {column.name}
                    </NativeSelectOption>
                  ))}
                </NativeSelect>
              </div>
              <div className="flex flex-col gap-1">
                <Label htmlFor="studio-aggregate">Aggregate</Label>
                <NativeSelect
                  id="studio-aggregate"
                  className="w-full"
                  value={aggregate}
                  onChange={(event) => setAggregate(event.target.value)}
                >
                  {AGGREGATES.map((option) => (
                    <NativeSelectOption key={option} value={option}>
                      {option}
                    </NativeSelectOption>
                  ))}
                </NativeSelect>
              </div>
              <div className="flex flex-col gap-1">
                <Label htmlFor="studio-topic">Filter: topic</Label>
                <NativeSelect
                  id="studio-topic"
                  className="w-full"
                  value={filterTopic}
                  onChange={(event) => setFilterTopic(event.target.value)}
                >
                  <NativeSelectOption value="">all</NativeSelectOption>
                  {(columns?.columns.find((c) => c.name === "Topic")?.options ?? []).map(
                    (option) => (
                      <NativeSelectOption key={option} value={option}>
                        {option}
                      </NativeSelectOption>
                    ),
                  )}
                </NativeSelect>
              </div>
              <div className="flex flex-col gap-1">
                <Label htmlFor="studio-tier">Filter: tier</Label>
                <NativeSelect
                  id="studio-tier"
                  className="w-full"
                  value={filterTier}
                  onChange={(event) => setFilterTier(event.target.value)}
                >
                  <NativeSelectOption value="">all</NativeSelectOption>
                  {["L", "M", "H"].map((option) => (
                    <NativeSelectOption key={option} value={option}>
                      {option}
                    </NativeSelectOption>
                  ))}
                </NativeSelect>
              </div>
            </>
          ) : (
            <div className="flex flex-col gap-1">
              <Label htmlFor="studio-metric">Metric</Label>
              <NativeSelect
                id="studio-metric"
                className="w-full"
                value={resultsMetric}
                onChange={(event) => setResultsMetric(event.target.value)}
              >
                {RESULTS_METRICS.map((option) => (
                  <NativeSelectOption key={option} value={option}>
                    {option}
                  </NativeSelectOption>
                ))}
              </NativeSelect>
            </div>
          )}
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => getSvg() && downloadSvg("chart.svg", getSvg() as SVGSVGElement)}
            disabled={!currentRows.length}
          >
            Export SVG
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => getSvg() && downloadPng("chart.png", getSvg() as SVGSVGElement)}
            disabled={!currentRows.length}
          >
            Export PNG
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => downloadCsv("chart.csv", currentRows)}
            disabled={!currentRows.length}
          >
            Export CSV
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => downloadJson("chart.json", { spec, rows: currentRows })}
            disabled={!currentRows.length}
          >
            Export JSON
          </Button>
        </div>

        <div ref={previewRef} className="rounded-2xl border p-4">
          {busy ? (
            <p className="py-16 text-center text-sm text-muted-foreground">Loading…</p>
          ) : error ? (
            <p className="py-16 text-center text-sm text-destructive">
              Could not run the query. Check the column selection.
            </p>
          ) : currentRows.length === 0 ? (
            <p className="py-16 text-center text-sm text-muted-foreground">
              No data for this selection.
            </p>
          ) : (
            <ChartRenderer spec={spec} className="h-80 w-full" />
          )}
        </div>

        <Separator />

        <div className="flex flex-col gap-3">
          <p className="text-xs tracking-wide text-muted-foreground uppercase">Saved views</p>
          <div className="flex flex-wrap items-center gap-2">
            <Input
              placeholder="Name this view…"
              value={savedName}
              onChange={(event) => setSavedName(event.target.value)}
              className="max-w-64"
            />
            <Button size="sm" onClick={handleSave} disabled={!savedName.trim()}>
              Save view
            </Button>
          </div>
          <div className="flex flex-wrap gap-2">
            {(views.data ?? []).map((view) => (
              <span
                key={view.id}
                className="inline-flex items-center gap-1 rounded-full border px-3 py-1 text-xs"
              >
                <button type="button" className="hover:underline" onClick={() => handleLoad(view)}>
                  {view.name}
                </button>
                <button
                  type="button"
                  aria-label={`Delete ${view.name}`}
                  className="text-muted-foreground hover:text-destructive"
                  onClick={() => {
                    deleteView.mutate(view.name);
                    setTimeout(() => views.refetch(), 200);
                  }}
                >
                  ×
                </button>
              </span>
            ))}
            {(views.data ?? []).length === 0 ? (
              <span className="text-xs text-muted-foreground">No saved views yet.</span>
            ) : null}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
