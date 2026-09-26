import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@humanity-erp/ui";
import { useMetrics } from "../api/hooks";
import { useSource } from "../lib/source-context";
import { cellIntensity, classMetrics } from "../lib/metrics";
import { PanelMessage, PanelSkeleton } from "./panel-states";

interface MetricsPayload {
  confusion_matrix?: number[][];
  labels?: string[];
  precision_macro?: number;
  recall_macro?: number;
  f1_macro?: number;
}

const CELL = "68,114,196";

export function ClassificationQuality() {
  const { sourceId } = useSource();
  const { data, isLoading, isError } = useMetrics(sourceId);

  if (isLoading) return <PanelSkeleton title="Classification quality" />;
  if (isError || !data) {
    return (
      <PanelMessage
        title="Classification quality"
        message="No metrics yet — train a model first."
      />
    );
  }

  const metrics = data.metrics as MetricsPayload;
  const confusion = metrics.confusion_matrix ?? [];
  const labels = metrics.labels ?? [];

  if (confusion.length === 0 || labels.length === 0) {
    return (
      <PanelMessage
        title="Classification quality"
        message="No confusion matrix in the model metadata."
      />
    );
  }

  const maximum = Math.max(...confusion.flat());
  const classRows = classMetrics(confusion, labels);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Classification quality</CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col gap-6 lg:flex-row">
        <div className="flex-1">
          <p className="mb-2 text-xs tracking-wide text-muted-foreground uppercase">
            Confusion matrix (rows: actual)
          </p>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead />
                {labels.map((label) => (
                  <TableHead key={label} className="text-center">
                    {label}
                  </TableHead>
                ))}
              </TableRow>
            </TableHeader>
            <TableBody>
              {confusion.map((row, rowIndex) => (
                <TableRow key={labels[rowIndex]}>
                  <TableHead>{labels[rowIndex]}</TableHead>
                  {row.map((value, columnIndex) => (
                    <TableCell key={columnIndex} className="text-center">
                      <span
                        className="inline-flex size-8 items-center justify-center rounded-lg"
                        style={{
                          backgroundColor: `rgba(${CELL}, ${cellIntensity(value, maximum).toFixed(2)})`,
                        }}
                      >
                        {value}
                      </span>
                    </TableCell>
                  ))}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>

        <div className="flex-1">
          <p className="mb-2 text-xs tracking-wide text-muted-foreground uppercase">
            Per-class metrics
          </p>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Class</TableHead>
                <TableHead>Precision</TableHead>
                <TableHead>Recall</TableHead>
                <TableHead>F1</TableHead>
                <TableHead>Support</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {classRows.map((row) => (
                <TableRow key={row.label}>
                  <TableCell className="font-medium">{row.label}</TableCell>
                  <TableCell>{(row.precision * 100).toFixed(1)}%</TableCell>
                  <TableCell>{(row.recall * 100).toFixed(1)}%</TableCell>
                  <TableCell>{(row.f1 * 100).toFixed(1)}%</TableCell>
                  <TableCell>{row.support}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
          <p className="mt-3 text-xs text-muted-foreground">
            Macro F1 {((metrics.f1_macro ?? 0) * 100).toFixed(1)}% · precision{" "}
            {((metrics.precision_macro ?? 0) * 100).toFixed(1)}% · recall{" "}
            {((metrics.recall_macro ?? 0) * 100).toFixed(1)}%
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
