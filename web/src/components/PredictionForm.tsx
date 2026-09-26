import { type FormEvent, useEffect, useState } from "react";
import {
  Alert,
  AlertDescription,
  Badge,
  Button,
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  Field,
  FieldGroup,
  FieldLabel,
  Input,
  NativeSelect,
  NativeSelectOption,
  Skeleton,
} from "@humanity-erp/ui";
import { useModelFeatures, usePredict } from "../api/hooks";
import { useSource } from "../lib/source-context";
import { predictionRows } from "../lib/predict";
import type { PredictionRequest } from "../types";

/** Prediction form generated from the served model's feature metadata. */
export function PredictionForm() {
  const { sourceId } = useSource();
  const features = useModelFeatures(sourceId);
  const predict = usePredict(sourceId);
  const [values, setValues] = useState<Record<string, string | number>>({});

  useEffect(() => {
    const data = features.data;
    if (!data) return;
    setValues((current) => {
      const next: Record<string, string | number> = {};
      for (const name of data.features) {
        if (current[name] !== undefined) {
          next[name] = current[name];
        } else if (data.categorical.includes(name)) {
          next[name] = data.options[name]?.[0] ?? "";
        } else {
          next[name] = 0;
        }
      }
      return next;
    });
  }, [features.data]);

  const update = (name: string, value: string | number) =>
    setValues((current) => ({ ...current, [name]: value }));

  const onSubmit = (event: FormEvent) => {
    event.preventDefault();
    predict.mutate(values as unknown as PredictionRequest);
  };

  if (features.isLoading) return <Skeleton className="h-64 w-full" />;
  if (features.isError || !features.data) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Predict a support band</CardTitle>
        </CardHeader>
        <CardContent>
          <Alert>
            <AlertDescription>
              No model for source “{sourceId}”. Train one from the Datasets tab or with `make train
              SOURCE={sourceId}`.
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  const data = features.data;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Predict a support band ({sourceId})</CardTitle>
        <CardDescription>
          Send the {data.features.length} features to the {data.source} model and read the support
          band back.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={onSubmit} className="flex flex-col gap-4">
          <FieldGroup className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {data.features.map((name) =>
              data.categorical.includes(name) ? (
                <Field key={name}>
                  <FieldLabel htmlFor={name}>{name}</FieldLabel>
                  <NativeSelect
                    id={name}
                    className="w-full"
                    value={String(values[name] ?? "")}
                    onChange={(event) => update(name, event.target.value)}
                  >
                    {(data.options[name] ?? [String(values[name] ?? "")]).map((option) => (
                      <NativeSelectOption key={option} value={option}>
                        {option}
                      </NativeSelectOption>
                    ))}
                  </NativeSelect>
                </Field>
              ) : (
                <Field key={name}>
                  <FieldLabel htmlFor={name}>{name}</FieldLabel>
                  <Input
                    id={name}
                    type="number"
                    min={0}
                    value={Number(values[name] ?? 0)}
                    onChange={(event) => update(name, Number(event.target.value))}
                  />
                </Field>
              ),
            )}
          </FieldGroup>

          <div className="flex items-center gap-3">
            <Button type="submit" disabled={predict.isPending}>
              {predict.isPending ? "Predicting…" : "Predict"}
            </Button>
            {predict.isError ? (
              <span className="text-sm text-destructive">
                Prediction failed. Is a model trained for this source?
              </span>
            ) : null}
          </div>
        </form>

        {predict.data ? (
          <div className="mt-5 rounded-2xl border p-4">
            <div className="flex items-center gap-3">
              <span className="text-sm text-muted-foreground">Support band</span>
              <Badge>{predict.data.support_band}</Badge>
              <span className="text-xs text-muted-foreground">
                predicted class {predict.data.prediction}
              </span>
              <span className="text-sm text-muted-foreground">
                confidence {(predict.data.confidence * 100).toFixed(0)}%
              </span>
            </div>
            <div className="mt-3 flex flex-col gap-2">
              {predictionRows(predict.data.probabilities).map((row) => (
                <div key={row.label} className="flex items-center gap-3 text-sm">
                  <span className="w-16 font-medium">{row.label}</span>
                  <div className="h-2 flex-1 overflow-hidden rounded-full bg-muted">
                    <div
                      className="h-full rounded-full bg-primary"
                      style={{ width: `${row.percent}%` }}
                    />
                  </div>
                  <span className="w-10 text-right tabular-nums text-muted-foreground">
                    {row.percent}%
                  </span>
                </div>
              ))}
            </div>
          </div>
        ) : null}
      </CardContent>
    </Card>
  );
}
