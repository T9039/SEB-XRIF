import type { ChartData, ChartOptions } from "chart.js";
import {
  ArcElement,
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LinearScale,
  Tooltip,
} from "chart.js";
import { Bar, Doughnut } from "react-chartjs-2";

ChartJS.register(ArcElement, BarElement, CategoryScale, LinearScale, Tooltip, Legend);

/**
 * The single chart wrapper. Every dashboard chart goes through here so the
 * charting library (Chart.js) can be swapped for another without touching
 * component code.
 */
export function BarChart({
  data,
  options,
}: {
  data: ChartData<"bar">;
  options?: ChartOptions<"bar">;
}) {
  return <Bar data={data} options={options} />;
}

export function DoughnutChart({
  data,
  options,
}: {
  data: ChartData<"doughnut">;
  options?: ChartOptions<"doughnut">;
}) {
  return <Doughnut data={data} options={options} />;
}
