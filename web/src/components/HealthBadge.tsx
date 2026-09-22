import { Badge } from "@humanity-erp/ui";
import { useHealth } from "../api/hooks";

export function HealthBadge() {
  const { data, isLoading, isError } = useHealth();

  if (isLoading) return <Badge variant="secondary">checking…</Badge>;
  if (isError) return <Badge variant="destructive">api unreachable</Badge>;
  if (data?.model_loaded) return <Badge>model: {data.model_version}</Badge>;
  return <Badge variant="outline">no model trained</Badge>;
}
