import type { ChartConfig } from "@humanity-erp/ui";

/** Shared categorical palette (distinct, print-friendly). */
export const PALETTE = [
  "#4472C4",
  "#ED7D31",
  "#70AD47",
  "#9E6BB5",
  "#17A2B8",
  "#E15759",
  "#F28E2B",
  "#76B7B2",
  "#59A14F",
  "#B07AA1",
  "#4E79A7",
  "#A0CBE8",
];

/** Build a Recharts/shadcn ChartConfig for a list of series keys. */
export function chartConfig(series: string[], labels?: Record<string, string>): ChartConfig {
  const config: ChartConfig = {};
  series.forEach((key, index) => {
    config[key] = {
      label: labels?.[key] ?? key,
      color: PALETTE[index % PALETTE.length],
    };
  });
  return config;
}

/** The colour for a series at a given index. */
export function seriesColor(index: number): string {
  return PALETTE[index % PALETTE.length];
}
