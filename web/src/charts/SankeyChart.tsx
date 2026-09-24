import { Sankey, Tooltip } from "recharts";
import type { ChartSpec } from "./ChartRenderer";

interface SankeyExtra {
  nodes?: { name: string }[];
  links?: { source: number; target: number; value: number }[];
}

/** Flow diagram (e.g. stage -> topic -> tier) rendered with Recharts Sankey. */
export function SankeyChart({ spec, className = "" }: { spec: ChartSpec; className?: string }) {
  const extra = (spec.extra ?? {}) as SankeyExtra;
  const nodes = extra.nodes ?? [];
  const links = extra.links ?? [];

  if (nodes.length === 0 || links.length === 0) {
    return <p className="text-sm text-muted-foreground">No flow data</p>;
  }

  return (
    <div className={`w-full overflow-x-auto ${className}`}>
      <Sankey
        width={640}
        height={288}
        data={{ nodes, links }}
        nodePadding={14}
        margin={{ left: 8, right: 8, top: 8, bottom: 8 }}
      >
        <Tooltip />
      </Sankey>
    </div>
  );
}
