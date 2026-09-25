import { type FormEvent, useEffect, useState } from "react";
import {
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
} from "@humanity-erp/ui";
import { useOptions, usePredict } from "../api/hooks";
import { predictionRows } from "../lib/predict";
import type { PredictionRequest } from "../types";

const CATEGORICAL_FIELDS: { name: keyof PredictionRequest; label: string }[] = [
  { name: "gender", label: "Gender" },
  { name: "NationalITy", label: "Nationality" },
  { name: "PlaceofBirth", label: "Place of birth" },
  { name: "StageID", label: "Stage" },
  { name: "GradeID", label: "Grade" },
  { name: "SectionID", label: "Section" },
  { name: "Topic", label: "Topic" },
  { name: "Semester", label: "Semester" },
  { name: "Relation", label: "Relation" },
  { name: "ParentAnsweringSurvey", label: "Parent answered survey" },
  { name: "ParentschoolSatisfaction", label: "Parent school satisfaction" },
  { name: "StudentAbsenceDays", label: "Absence days" },
];

const NUMERIC_FIELDS: { name: keyof PredictionRequest; label: string }[] = [
  { name: "raisedhands", label: "Raised hands" },
  { name: "VisITedResources", label: "Visited resources" },
  { name: "AnnouncementsView", label: "Announcements viewed" },
  { name: "Discussion", label: "Discussion" },
];

const DEFAULTS: Record<string, string | number> = {
  gender: "M",
  NationalITy: "KW",
  PlaceofBirth: "KuwaIT",
  StageID: "lowerlevel",
  GradeID: "G-04",
  SectionID: "A",
  Topic: "IT",
  Semester: "F",
  Relation: "Father",
  ParentAnsweringSurvey: "Yes",
  ParentschoolSatisfaction: "Good",
  StudentAbsenceDays: "Under-7",
  raisedhands: 15,
  VisITedResources: 16,
  AnnouncementsView: 2,
  Discussion: 20,
};

export function PredictionForm() {
  const { data: optionsData } = useOptions();
  const predict = usePredict();
  const [values, setValues] = useState<Record<string, string | number>>(DEFAULTS);

  useEffect(() => {
    if (!optionsData) return;
    setValues((current) => {
      const next = { ...current };
      for (const [field, options] of Object.entries(optionsData.options)) {
        if (next[field] === undefined && options.length > 0) {
          next[field] = options[0];
        }
      }
      return next;
    });
  }, [optionsData]);

  const update = (name: string, value: string | number) =>
    setValues((current) => ({ ...current, [name]: value }));

  const onSubmit = (event: FormEvent) => {
    event.preventDefault();
    predict.mutate(values as unknown as PredictionRequest);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Predict a support band</CardTitle>
        <CardDescription>
          Send the 16 predictors to the model and read the support band back.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={onSubmit} className="flex flex-col gap-4">
          <FieldGroup className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {CATEGORICAL_FIELDS.map((field) => (
              <Field key={field.name}>
                <FieldLabel htmlFor={field.name}>{field.label}</FieldLabel>
                <NativeSelect
                  id={field.name}
                  className="w-full"
                  value={String(values[field.name] ?? "")}
                  onChange={(event) => update(field.name, event.target.value)}
                >
                  {(optionsData?.options[field.name] ?? [String(values[field.name] ?? "")]).map(
                    (option) => (
                      <NativeSelectOption key={option} value={option}>
                        {option}
                      </NativeSelectOption>
                    ),
                  )}
                </NativeSelect>
              </Field>
            ))}
            {NUMERIC_FIELDS.map((field) => (
              <Field key={field.name}>
                <FieldLabel htmlFor={field.name}>{field.label}</FieldLabel>
                <Input
                  id={field.name}
                  type="number"
                  min={0}
                  value={Number(values[field.name] ?? 0)}
                  onChange={(event) => update(field.name, Number(event.target.value))}
                />
              </Field>
            ))}
          </FieldGroup>

          <div className="flex items-center gap-3">
            <Button type="submit" disabled={predict.isPending}>
              {predict.isPending ? "Predicting…" : "Predict"}
            </Button>
            {predict.isError ? (
              <span className="text-sm text-destructive">
                Prediction failed. Is a model trained?
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
                  <span className="w-4 font-medium">{row.label}</span>
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
