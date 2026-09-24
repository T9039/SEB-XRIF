import type { ChartSpec } from "./ChartRenderer";
import { boxStats, numberAt } from "./data";
import { seriesColor } from "./color";

/** Box-and-whisker plot built from raw per-group values. */
export function BoxPlot({ spec, className = "" }: { spec: ChartSpec; className?: string }) {
  const xKey = spec.xKey ?? "x";
  const metric = spec.series[0] ?? "value";

  const groups = new Map<string, number[]>();
  for (const row of spec.rows) {
    const label = String(row[xKey] ?? "");
    const value = numberAt(row, metric);
    if (!Number.isFinite(value)) continue;
    groups.set(label, [...(groups.get(label) ?? []), value]);
  }

  const entries = [...groups.entries()].map(([label, values]) => ({
    label,
    stats: boxStats(values),
  }));
  if (entries.length === 0) {
    return <p className="text-sm text-muted-foreground">No data</p>;
  }

  const minimum = Math.min(...entries.map((entry) => entry.stats.min));
  const maximum = Math.max(...entries.map((entry) => entry.stats.max));
  const scale = (value: number) =>
    maximum === minimum ? 50 : ((value - minimum) / (maximum - minimum)) * 100;
  const color = seriesColor(0);

  return (
    <div className={`flex h-72 w-full flex-col justify-center gap-3 ${className}`}>
      {entries.map(({ label, stats }) => (
        <div key={label} className="flex items-center gap-3 text-xs">
          <span className="w-20 shrink-0 text-right text-muted-foreground">{label}</span>
          <div className="flex-1">
            <svg viewBox="0 0 100 6" preserveAspectRatio="none" className="h-6 w-full">
              <line
                x1={scale(stats.min)}
                x2={scale(stats.max)}
                y1="3"
                y2="3"
                stroke={color}
                strokeWidth="0.4"
              />
              <rect
                x={scale(stats.q1)}
                y="0.5"
                width={Math.max(0.6, scale(stats.q3) - scale(stats.q1))}
                height="5"
                fill={color}
                fillOpacity="0.3"
                stroke={color}
                strokeWidth="0.3"
              />
              <line
                x1={scale(stats.median)}
                x2={scale(stats.median)}
                y1="0.5"
                y2="5.5"
                stroke={color}
                strokeWidth="0.9"
              />
            </svg>
          </div>
          <span className="w-24 shrink-0 tabular-nums text-muted-foreground">
            med {stats.median.toFixed(1)}
          </span>
        </div>
      ))}
    </div>
  );
}
