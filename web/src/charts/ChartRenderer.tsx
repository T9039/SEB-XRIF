import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ComposedChart,
  Funnel,
  FunnelChart,
  Line,
  LineChart,
  Pie,
  PieChart,
  PolarAngleAxis,
  PolarGrid,
  PolarRadiusAxis,
  Radar,
  RadarChart,
  RadialBar,
  RadialBarChart,
  Scatter,
  ScatterChart,
  Treemap,
  XAxis,
  YAxis,
} from "recharts";
import {
  ChartContainer,
  ChartLegend,
  ChartLegendContent,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from "@humanity-erp/ui";
import { chartConfig } from "./color";
import type { Row } from "./data";
import { BoxPlot } from "./BoxPlot";
import { Heatmap } from "./Heatmap";
import { ParallelCoordinates } from "./ParallelCoordinates";
import { SankeyChart } from "./SankeyChart";

export type ChartType =
  | "bar"
  | "line"
  | "area"
  | "composed"
  | "scatter"
  | "radar"
  | "radial"
  | "pie"
  | "treemap"
  | "funnel"
  | "heatmap"
  | "box"
  | "parallel"
  | "sankey";

export interface ChartSpec {
  type: ChartType;
  rows: Row[];
  series: string[];
  xKey?: string;
  nameKey?: string;
  valueKey?: string;
  config?: ChartConfig;
  stacked?: boolean;
  horizontal?: boolean;
  curve?: "linear" | "natural" | "step";
  showLegend?: boolean;
  showGrid?: boolean;
  /** Extra payload for custom charts (heatmap matrix, sankey links, box groups). */
  extra?: Record<string, unknown>;
}

const AXIS = { tickLine: false, axisLine: false, tickMargin: 8 } as const;

export function ChartRenderer({
  spec,
  className = "h-72 w-full",
}: {
  spec: ChartSpec;
  className?: string;
}) {
  const config = spec.config ?? chartConfig(spec.series);
  const xKey = spec.xKey ?? "x";
  const legend = spec.showLegend ?? spec.series.length > 1;

  const tooltip = <ChartTooltip content={<ChartTooltipContent />} />;
  const legendNode = legend ? <ChartLegend content={<ChartLegendContent />} /> : null;
  const grid = spec.showGrid === false ? null : <CartesianGrid vertical={false} />;
  const curve = spec.curve ?? "natural";

  switch (spec.type) {
    case "bar":
      return (
        <ChartContainer config={config} className={className}>
          <BarChart data={spec.rows} layout={spec.horizontal ? "vertical" : "horizontal"}>
            {grid}
            {spec.horizontal ? (
              <>
                <YAxis dataKey={xKey} type="category" width={140} {...AXIS} />
                <XAxis type="number" {...AXIS} />
              </>
            ) : (
              <>
                <XAxis dataKey={xKey} {...AXIS} />
                <YAxis {...AXIS} />
              </>
            )}
            {tooltip}
            {legendNode}
            {spec.series.map((key) => (
              <Bar
                key={key}
                dataKey={key}
                fill={`var(--color-${key})`}
                stackId={spec.stacked ? "stack" : undefined}
                radius={4}
              />
            ))}
          </BarChart>
        </ChartContainer>
      );

    case "area":
      return (
        <ChartContainer config={config} className={className}>
          <AreaChart data={spec.rows}>
            {grid}
            <XAxis dataKey={xKey} {...AXIS} />
            <YAxis {...AXIS} />
            {tooltip}
            {legendNode}
            {spec.series.map((key) => (
              <Area
                key={key}
                dataKey={key}
                type={curve}
                fill={`var(--color-${key})`}
                fillOpacity={0.3}
                stroke={`var(--color-${key})`}
                stackId={spec.stacked ? "stack" : undefined}
              />
            ))}
          </AreaChart>
        </ChartContainer>
      );

    case "line":
      return (
        <ChartContainer config={config} className={className}>
          <LineChart data={spec.rows}>
            {grid}
            <XAxis dataKey={xKey} {...AXIS} />
            <YAxis {...AXIS} />
            {tooltip}
            {legendNode}
            {spec.series.map((key) => (
              <Line
                key={key}
                dataKey={key}
                type={curve}
                stroke={`var(--color-${key})`}
                strokeWidth={2}
                dot={false}
              />
            ))}
          </LineChart>
        </ChartContainer>
      );

    case "composed":
      return (
        <ChartContainer config={config} className={className}>
          <ComposedChart data={spec.rows}>
            {grid}
            <XAxis dataKey={xKey} {...AXIS} />
            <YAxis {...AXIS} />
            {tooltip}
            {legendNode}
            {spec.series.map((key, index) =>
              index === 0 ? (
                <Bar key={key} dataKey={key} fill={`var(--color-${key})`} radius={4} />
              ) : (
                <Line
                  key={key}
                  dataKey={key}
                  type={curve}
                  stroke={`var(--color-${key})`}
                  strokeWidth={2}
                  dot={false}
                />
              ),
            )}
          </ComposedChart>
        </ChartContainer>
      );

    case "scatter":
      return (
        <ChartContainer config={config} className={className}>
          <ScatterChart>
            {grid}
            <XAxis dataKey={xKey} type="number" {...AXIS} />
            <YAxis dataKey={spec.valueKey} type="number" {...AXIS} />
            {tooltip}
            {legendNode}
            {spec.series.map((key) => (
              <Scatter
                key={key}
                name={key}
                data={spec.rows}
                dataKey={key}
                fill={`var(--color-${key})`}
              />
            ))}
          </ScatterChart>
        </ChartContainer>
      );

    case "radar":
      return (
        <ChartContainer config={config} className={className}>
          <RadarChart data={spec.rows}>
            <PolarGrid />
            <PolarAngleAxis dataKey={xKey} />
            <PolarRadiusAxis />
            {tooltip}
            {legendNode}
            {spec.series.map((key) => (
              <Radar
                key={key}
                dataKey={key}
                stroke={`var(--color-${key})`}
                fill={`var(--color-${key})`}
                fillOpacity={0.4}
              />
            ))}
          </RadarChart>
        </ChartContainer>
      );

    case "radial":
      return (
        <ChartContainer config={config} className={className}>
          <RadialBarChart data={spec.rows} innerRadius="30%" outerRadius="90%">
            {tooltip}
            <RadialBar dataKey={spec.valueKey ?? "value"} />
          </RadialBarChart>
        </ChartContainer>
      );

    case "pie":
      return (
        <ChartContainer config={config} className={className}>
          <PieChart>
            {tooltip}
            {legendNode}
            <Pie
              data={spec.rows}
              dataKey={spec.valueKey ?? "value"}
              nameKey={spec.nameKey ?? "name"}
              innerRadius={55}
              outerRadius={90}
            >
              {spec.rows.map((_, index) => (
                <Cell key={index} fill={`var(--color-${spec.series[index] ?? index})`} />
              ))}
            </Pie>
          </PieChart>
        </ChartContainer>
      );

    case "treemap":
      return (
        <ChartContainer config={config} className={className}>
          <Treemap
            data={spec.rows}
            dataKey={spec.valueKey ?? "value"}
            nameKey={spec.nameKey ?? "name"}
            stroke="#fff"
            fill="var(--color-value)"
          />
        </ChartContainer>
      );

    case "funnel":
      return (
        <ChartContainer config={config} className={className}>
          <FunnelChart>
            {tooltip}
            <Funnel
              data={spec.rows}
              dataKey={spec.valueKey ?? "value"}
              nameKey={spec.nameKey ?? "name"}
            />
          </FunnelChart>
        </ChartContainer>
      );

    case "heatmap":
      return <Heatmap spec={spec} className={className} />;

    case "box":
      return <BoxPlot spec={spec} className={className} />;

    case "parallel":
      return <ParallelCoordinates spec={spec} className={className} />;

    case "sankey":
      return <SankeyChart spec={spec} className={className} />;

    default:
      return null;
  }
}
