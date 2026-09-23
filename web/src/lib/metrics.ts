/** Pure helpers for the classification-quality panels. */

export interface ClassMetric {
  label: string;
  precision: number;
  recall: number;
  f1: number;
  support: number;
}

/** Derive per-class precision/recall/F1 from a confusion matrix. */
export function classMetrics(confusion: number[][], labels: string[]): ClassMetric[] {
  const columnTotals = labels.map((_, column) =>
    confusion.reduce((sum, row) => sum + (row[column] ?? 0), 0),
  );
  const rowTotals = confusion.map((row) => row.reduce((sum, value) => sum + value, 0));

  return labels.map((label, index) => {
    const truePositive = confusion[index]?.[index] ?? 0;
    const precision = columnTotals[index] ? truePositive / columnTotals[index] : 0;
    const recall = rowTotals[index] ? truePositive / rowTotals[index] : 0;
    const f1 = precision + recall ? (2 * precision * recall) / (precision + recall) : 0;
    return { label, precision, recall, f1, support: rowTotals[index] ?? 0 };
  });
}

/** Return a 0–1 intensity for a confusion-matrix cell. */
export function cellIntensity(value: number, maximum: number): number {
  return maximum > 0 ? value / maximum : 0;
}
