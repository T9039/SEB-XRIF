import type { Meta, StoryObj } from "@storybook/react";
import { CartesianGrid, Line, LineChart, XAxis, YAxis } from "recharts";
import {
  ChartContainer,
  ChartLegend,
  ChartLegendContent,
  ChartTooltip,
  ChartTooltipContent,
} from "./chart";

const meta = {
  title: "UI/Chart",
  component: ChartContainer,
  parameters: { layout: "centered" },
  tags: ["autodocs"],
} satisfies Meta<typeof ChartContainer>;

export default meta;
type Story = StoryObj<typeof meta>;

const revenue = [
  { month: "Jan", revenue: 186, expenses: 80 },
  { month: "Feb", revenue: 305, expenses: 200 },
  { month: "Mar", revenue: 237, expenses: 120 },
  { month: "Apr", revenue: 73, expenses: 190 },
  { month: "May", revenue: 209, expenses: 130 },
  { month: "Jun", revenue: 214, expenses: 140 },
];

const config = {
  revenue: { label: "Revenue", color: "#2563eb" },
  expenses: { label: "Expenses", color: "#f97316" },
} as const;

export const LineChartStory: Story = {
  render: () => (
    <div className="w-96 rounded-3xl border p-4">
      <ChartContainer config={config} className="h-56">
        <LineChart data={revenue} accessibilityLayer>
          <CartesianGrid vertical={false} />
          <XAxis dataKey="month" tickLine={false} axisLine={false} tickMargin={8} />
          <YAxis tickLine={false} axisLine={false} tickMargin={8} />
          <ChartTooltip cursor={false} content={<ChartTooltipContent />} />
          <Line
            dataKey="revenue"
            type="natural"
            stroke="var(--color-revenue)"
            strokeWidth={2}
            dot={false}
          />
          <Line
            dataKey="expenses"
            type="natural"
            stroke="var(--color-expenses)"
            strokeWidth={2}
            dot={false}
          />
        </LineChart>
      </ChartContainer>
      <ChartLegend content={<ChartLegendContent />} />
    </div>
  ),
};
