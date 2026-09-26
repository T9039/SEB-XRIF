import { Card, CardContent, CardHeader, CardTitle, Skeleton } from "@humanity-erp/ui";
import { useMetrics } from "../api/hooks";
import { useSource } from "../lib/source-context";

function format(value: unknown): string {
  if (typeof value === "number") {
    return value <= 1 ? `${(value * 100).toFixed(1)}%` : value.toFixed(2);
  }
  return "—";
}

export function MetricCards() {
  const { sourceId } = useSource();
  const { data, isLoading, isError } = useMetrics(sourceId);

  if (isError) {
    return (
      <Card>
        <CardContent className="pt-(--card-spacing) text-sm text-muted-foreground">
          No metrics yet — train a model to populate this panel.
        </CardContent>
      </Card>
    );
  }

  const metrics = (data?.metrics ?? {}) as Record<string, unknown>;
  const cv = metrics.cv as { mean?: number } | undefined;

  const cards = [
    { label: "Accuracy", value: format(metrics.accuracy) },
    { label: "Macro F1", value: format(metrics.f1_macro) },
    { label: "CV macro F1", value: format(cv?.mean) },
    { label: "Model", value: data?.model ?? "—" },
  ];

  return (
    <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
      {cards.map((card) => (
        <Card key={card.label} size="sm">
          <CardHeader>
            <CardTitle className="text-xs tracking-wide text-muted-foreground uppercase">
              {card.label}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-7 w-20" />
            ) : (
              <span className="font-heading text-2xl font-semibold">{card.value}</span>
            )}
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
