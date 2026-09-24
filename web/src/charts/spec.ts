import { chartConfig } from "./color";
import type { ChartSpec, ChartType } from "./ChartRenderer";
import type { Row } from "./data";

export interface StudioConfig {
  type: ChartType;
  x: string;
  y: string;
  group: string;
  aggregate: string;
  source: "learners" | "results";
}

/** Chart types that consume a long `{name, value}` table. */
export const LONG_TYPES: ChartType[] = ["pie", "treemap", "funnel", "radial"];

/** Turn a Studio configuration plus query output into a ChartSpec. */
export function buildChartSpec(
  config: StudioConfig,
  queryRows: Row[],
  querySeries: string[],
): ChartSpec {
  const { type, group, y } = config;
  const valueLabel = config.aggregate === "count" ? "count" : y || "count";

  if (LONG_TYPES.includes(type)) {
    const long: Row[] = queryRows.map((row) => ({
      name: String(row.x ?? ""),
      value: Number(row.value ?? 0),
    }));
    if (type === "pie") {
      const names = long.map((row) => String(row.name));
      return {
        type,
        rows: long,
        series: names,
        nameKey: "name",
        valueKey: "value",
        config: chartConfig(names),
        showLegend: true,
      };
    }
    return {
      type,
      rows: long,
      series: ["value"],
      nameKey: "name",
      valueKey: "value",
      config: chartConfig(["value"], { value: valueLabel }),
    };
  }

  if (group && querySeries.length > 0) {
    return {
      type,
      rows: queryRows,
      series: querySeries,
      xKey: "x",
      stacked: type === "bar",
      showLegend: true,
    };
  }

  return {
    type,
    rows: queryRows.map((row) => ({ x: row.x ?? "", value: Number(row.value ?? 0) })),
    series: ["value"],
    xKey: "x",
    config: chartConfig(["value"], { value: valueLabel }),
    showLegend: false,
  };
}
