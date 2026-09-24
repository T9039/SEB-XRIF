import { CartesianGrid, Scatter, ScatterChart, XAxis, YAxis } from "recharts";
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from "@humanity-erp/ui";
import { chartConfig } from "./color";

export interface EmbeddingPoint {
  x: number;
  y: number;
  tier: string;
  cluster: number;
}

/** PCA projection coloured by performance tier. */
export function EmbeddingScatter({
  points,
  tiers,
  className = "h-72 w-full",
}: {
  points: EmbeddingPoint[];
  tiers: string[];
  className?: string;
}) {
  const config: ChartConfig = chartConfig(tiers);
  return (
    <ChartContainer config={config} className={className}>
      <ScatterChart>
        <CartesianGrid />
        <XAxis type="number" dataKey="x" name="PC1" tickLine={false} axisLine={false} />
        <YAxis type="number" dataKey="y" name="PC2" tickLine={false} axisLine={false} />
        <ChartTooltip content={<ChartTooltipContent />} />
        {tiers.map((tier) => (
          <Scatter
            key={tier}
            name={tier}
            data={points.filter((point) => point.tier === tier)}
            fill={`var(--color-${tier})`}
          />
        ))}
      </ScatterChart>
    </ChartContainer>
  );
}
