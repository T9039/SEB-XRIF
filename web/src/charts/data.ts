/** Pure helpers shared by the chart components. */

export type Row = Record<string, string | number | null>;

export interface BoxStats {
  min: number;
  q1: number;
  median: number;
  q3: number;
  max: number;
}

/** Numeric value keys in a set of wide rows, excluding the x axis. */
export function numericKeys(rows: Row[], exclude: string[] = ["x", "name", "axis"]): string[] {
  const keys = new Set<string>();
  for (const row of rows) {
    for (const [key, value] of Object.entries(row)) {
      if (!exclude.includes(key) && typeof value === "number") {
        keys.add(key);
      }
    }
  }
  return [...keys];
}

function quantile(sorted: number[], p: number): number {
  if (sorted.length === 0) return 0;
  const index = (sorted.length - 1) * p;
  const lower = Math.floor(index);
  const upper = Math.ceil(index);
  return sorted[lower] + (sorted[upper] - sorted[lower]) * (index - lower);
}

/** Five-number summary for a set of values. */
export function boxStats(values: number[]): BoxStats {
  const sorted = [...values].filter((value) => Number.isFinite(value)).sort((a, b) => a - b);
  if (sorted.length === 0) {
    return { min: 0, q1: 0, median: 0, q3: 0, max: 0 };
  }
  return {
    min: sorted[0],
    q1: quantile(sorted, 0.25),
    median: quantile(sorted, 0.5),
    q3: quantile(sorted, 0.75),
    max: sorted[sorted.length - 1],
  };
}

/** Scale a value from a domain into a 0–1 range, clamped. */
export function normalize(value: number, min: number, max: number): number {
  if (max === min) return 0;
  return Math.min(1, Math.max(0, (value - min) / (max - min)));
}

/** Read a numeric field from a row, defaulting to NaN. */
export function numberAt(row: Row, key: string): number {
  const value = row[key];
  return typeof value === "number" ? value : Number.NaN;
}
