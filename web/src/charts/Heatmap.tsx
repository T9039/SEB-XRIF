import type { ChartSpec } from "./ChartRenderer";

interface HeatmapExtra {
  matrix?: number[][];
  rowLabels?: string[];
  colLabels?: string[];
}

/** Correlation/confusion-style heatmap rendered as a labelled grid. */
export function Heatmap({ spec, className = "" }: { spec: ChartSpec; className?: string }) {
  const extra = (spec.extra ?? {}) as HeatmapExtra;
  const matrix = extra.matrix ?? [];
  const rowLabels = extra.rowLabels ?? [];
  const colLabels = extra.colLabels ?? [];

  if (matrix.length === 0) {
    return <p className="text-sm text-muted-foreground">No data</p>;
  }

  const flat = matrix.flat();
  const min = Math.min(...flat);
  const max = Math.max(...flat);
  const intensity = (value: number) =>
    max === min ? 0.2 : 0.06 + 0.94 * ((value - min) / (max - min));

  return (
    <div className={`overflow-x-auto ${className}`}>
      <table className="border-separate border-spacing-1 text-xs">
        <thead>
          <tr>
            <th />
            {colLabels.map((label) => (
              <th key={label} className="pb-1 font-medium text-muted-foreground">
                {label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {matrix.map((row, rowIndex) => (
            <tr key={rowLabels[rowIndex] ?? rowIndex}>
              <th className="pr-2 text-right font-medium text-muted-foreground">
                {rowLabels[rowIndex] ?? rowIndex}
              </th>
              {row.map((value, colIndex) => (
                <td key={colIndex}>
                  <div
                    className="flex h-9 min-w-10 items-center justify-center rounded"
                    style={{
                      backgroundColor: `rgba(68,114,196,${intensity(value).toFixed(2)})`,
                    }}
                    title={`${rowLabels[rowIndex]} / ${colLabels[colIndex]}: ${value}`}
                  >
                    {value.toFixed(2)}
                  </div>
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
