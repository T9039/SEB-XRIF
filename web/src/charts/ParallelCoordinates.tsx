import type { ChartSpec } from "./ChartRenderer";
import { numberAt } from "./data";
import { seriesColor } from "./color";

interface ParallelExtra {
  axes?: string[];
  colorKey?: string;
}

/** Parallel-coordinates plot for comparing many numeric predictors. */
export function ParallelCoordinates({
  spec,
  className = "",
}: {
  spec: ChartSpec;
  className?: string;
}) {
  const extra = (spec.extra ?? {}) as ParallelExtra;
  const axes = extra.axes ?? spec.series;
  const rows = spec.rows;

  if (axes.length === 0 || rows.length === 0) {
    return <p className="text-sm text-muted-foreground">No data</p>;
  }

  const domains = axes.map((axis) => {
    const values = rows.map((row) => numberAt(row, axis)).filter(Number.isFinite);
    return [Math.min(...values), Math.max(...values)] as const;
  });

  const categories = extra.colorKey
    ? [...new Set(rows.map((row) => String(row[extra.colorKey as string])))]
    : ["all"];

  const width = 100;
  const height = 100;
  const xAt = (index: number) =>
    axes.length === 1 ? width / 2 : (index / (axes.length - 1)) * width;
  const yAt = (value: number, index: number) => {
    const [low, high] = domains[index];
    return height - (high === low ? 0.5 : (value - low) / (high - low)) * height;
  };

  return (
    <div className={`flex h-72 w-full flex-col gap-2 ${className}`}>
      <svg viewBox={`0 0 ${width} ${height}`} preserveAspectRatio="none" className="min-h-0 flex-1">
        {axes.map((axis, index) => (
          <line
            key={axis}
            x1={xAt(index)}
            x2={xAt(index)}
            y1="0"
            y2={height}
            stroke="#d4d4d4"
            strokeWidth="0.3"
          />
        ))}
        {rows.map((row, rowIndex) => {
          const category = extra.colorKey ? String(row[extra.colorKey]) : "all";
          const color = seriesColor(categories.indexOf(category));
          const points = axes
            .map((axis, index) => `${xAt(index)},${yAt(numberAt(row, axis), index)}`)
            .join(" ");
          return (
            <polyline
              key={rowIndex}
              points={points}
              fill="none"
              stroke={color}
              strokeWidth="0.3"
              opacity="0.35"
            />
          );
        })}
      </svg>
      <div className="flex flex-wrap gap-3 text-xs text-muted-foreground">
        {axes.map((axis) => (
          <span key={axis}>{axis}</span>
        ))}
      </div>
    </div>
  );
}
