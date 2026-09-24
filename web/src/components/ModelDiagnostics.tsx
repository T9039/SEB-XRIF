import type { ReactNode } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@humanity-erp/ui";
import { useDiagnostics } from "../api/hooks";
import { ChartRenderer } from "../charts/ChartRenderer";
import { PanelMessage, PanelSkeleton } from "./panel-states";

function mean(values: number[]): number {
  return values.length ? values.reduce((sum, value) => sum + value, 0) / values.length : 0;
}

function CurveBlock({ title, children }: { title: string; children: ReactNode }) {
  return (
    <div>
      <p className="mb-2 text-xs tracking-wide text-muted-foreground uppercase">{title}</p>
      {children}
    </div>
  );
}

export function ModelDiagnostics() {
  const { data, isLoading, isError } = useDiagnostics();

  if (isLoading) return <PanelSkeleton title="Model diagnostics" />;
  if (isError || !data) {
    return (
      <PanelMessage
        title="Model diagnostics"
        message="Train a model to compute ROC, PR, calibration, and learning curves."
      />
    );
  }

  const summary =
    `macro AUC ${data.macro_auc.toFixed(3)} · ` +
    `mean AP ${mean(Object.values(data.average_precision)).toFixed(3)} · ` +
    `mean Brier ${mean(Object.values(data.brier)).toFixed(3)}`;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Model diagnostics</CardTitle>
        <CardDescription>{summary}</CardDescription>
      </CardHeader>
      <CardContent className="grid gap-6 lg:grid-cols-2">
        <CurveBlock title="ROC (one-vs-rest)">
          <ChartRenderer
            spec={{
              type: "line",
              rows: data.roc,
              series: data.classes,
              xKey: "x",
              curve: "linear",
            }}
            className="h-56 w-full"
          />
        </CurveBlock>
        <CurveBlock title="Precision–Recall">
          <ChartRenderer
            spec={{ type: "line", rows: data.pr, series: data.classes, xKey: "x", curve: "linear" }}
            className="h-56 w-full"
          />
        </CurveBlock>
        <CurveBlock title="Calibration (reliability)">
          <ChartRenderer
            spec={{
              type: "line",
              rows: data.calibration,
              series: data.classes,
              xKey: "x",
              curve: "linear",
            }}
            className="h-56 w-full"
          />
        </CurveBlock>
        <CurveBlock title="Learning curve">
          <ChartRenderer
            spec={{
              type: "line",
              rows: data.learning,
              series: ["train", "test"],
              xKey: "x",
              curve: "linear",
            }}
            className="h-56 w-full"
          />
        </CurveBlock>
      </CardContent>
    </Card>
  );
}
