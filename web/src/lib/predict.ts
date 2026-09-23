/** Pure helpers for the prediction panels. */

export interface PredictionRow {
  label: string;
  percent: number;
}

/** Turn a probability map into rows sorted most-likely first. */
export function predictionRows(probabilities: Record<string, number>): PredictionRow[] {
  return Object.entries(probabilities)
    .map(([label, value]) => ({ label, percent: Math.round(value * 100) }))
    .sort((a, b) => b.percent - a.percent);
}
