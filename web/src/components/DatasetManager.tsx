import { useState } from "react";
import type { FormEvent } from "react";
import { useQueryClient } from "@tanstack/react-query";
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
  Input,
  Label,
  NativeSelect,
  NativeSelectOption,
  Textarea,
} from "@humanity-erp/ui";
import {
  useCheckDataset,
  useDatasets,
  useDeleteDataset,
  useTrainDataset,
  useUploadDataset,
} from "../api/hooks";
import { PanelSkeleton } from "./panel-states";

function message(error: unknown): string {
  const detail = (error as { response?: { data?: { error?: { message?: unknown } } } })?.response
    ?.data?.error?.message;
  if (typeof detail === "string") return detail;
  if (detail && typeof detail === "object") {
    const obj = detail as { message?: string; missing?: string[]; columns?: string[] };
    const parts = [obj.message];
    if (obj.missing?.length) parts.push(`missing: ${obj.missing.join(", ")}`);
    if (obj.columns?.length) parts.push(`columns: ${obj.columns.join(", ")}`);
    return parts.filter(Boolean).join(" — ");
  }
  return String(error);
}

/** Check a dataset, adapt it if needed, upload, train, and manage sources. */
export function DatasetManager() {
  const client = useQueryClient();
  const datasets = useDatasets();
  const check = useCheckDataset();
  const upload = useUploadDataset();
  const remove = useDeleteDataset();
  const train = useTrainDataset();

  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [target, setTarget] = useState("Class");
  const [classLabels, setClassLabels] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [mapping, setMapping] = useState("");
  const [trainAfter, setTrainAfter] = useState(true);
  const [mode, setMode] = useState("single");
  const [model, setModel] = useState("random_forest");
  const [error, setError] = useState("");

  const refresh = () => client.invalidateQueries({ queryKey: ["datasets"] });

  const onPick = async (picked: File | null) => {
    setFile(picked);
    setError("");
    if (!picked) return;
    try {
      const report = await check.mutateAsync(picked);
      if (report.kind === "table" && report.adaptable && report.suggested_mapping) {
        if (report.suggested_mapping.target) setTarget(report.suggested_mapping.target);
        setMapping(JSON.stringify(report.suggested_mapping, null, 2));
      }
    } catch (err) {
      setError(message(err));
    }
  };

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setError("");
    if (!file) {
      setError("Choose a file (.json, .jsonl, .csv or .tsv).");
      return;
    }
    try {
      await upload.mutateAsync({
        name,
        description,
        target,
        classLabels,
        mapping,
        train: trainAfter,
        mode,
        model,
        file,
      });
      setName("");
      setDescription("");
      setFile(null);
      setMapping("");
      await refresh();
    } catch (err) {
      setError(message(err));
    }
  };

  const onTrain = async (sourceName: string) => {
    setError("");
    try {
      await train.mutateAsync({
        name: sourceName,
        mode: mode === "single" ? "single" : "matrix",
        model: mode === "single" ? model : undefined,
      });
      await refresh();
    } catch (err) {
      setError(message(err));
    }
  };

  const onDelete = async (sourceName: string) => {
    setError("");
    try {
      await remove.mutateAsync(sourceName);
      await refresh();
    } catch (err) {
      setError(message(err));
    }
  };

  const report = check.data;

  return (
    <div className="flex flex-col gap-4">
      <Card>
        <CardHeader>
          <CardTitle>Add a dataset</CardTitle>
          <CardDescription>
            A profile-conformant xAPI statements file (.json/.jsonl), or a table (.csv/.tsv) adapted
            with a column mapping. Data only — nothing is executed.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={onSubmit} className="flex flex-col gap-4">
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              <div className="flex flex-col gap-1">
                <Label htmlFor="ds-name">Name</Label>
                <Input
                  id="ds-name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                />
              </div>
              <div className="flex flex-col gap-1">
                <Label htmlFor="ds-target">Target column</Label>
                <Input id="ds-target" value={target} onChange={(e) => setTarget(e.target.value)} />
              </div>
              <div className="flex flex-col gap-1">
                <Label htmlFor="ds-labels">Class labels</Label>
                <Input
                  id="ds-labels"
                  placeholder="L,M,H"
                  value={classLabels}
                  onChange={(e) => setClassLabels(e.target.value)}
                />
              </div>
              <div className="flex flex-col gap-1">
                <Label htmlFor="ds-file">File (.json/.jsonl/.csv/.tsv)</Label>
                <Input
                  id="ds-file"
                  type="file"
                  accept=".json,.jsonl,.csv,.tsv"
                  onChange={(e) => onPick(e.target.files?.[0] ?? null)}
                />
              </div>
            </div>
            <div className="flex flex-col gap-1">
              <Label htmlFor="ds-description">Description</Label>
              <Input
                id="ds-description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />
            </div>

            {report ? (
              <Alert>
                <AlertDescription>
                  {report.conformant
                    ? "Profile-conformant — it will be accepted as-is."
                    : report.adaptable
                      ? `Adaptable (${report.kind}) — review the mapping below.`
                      : `Not adaptable: ${report.reason ?? report.missing?.join("; ")}`}
                </AlertDescription>
              </Alert>
            ) : null}

            {report?.kind === "table" && report.adaptable ? (
              <div className="flex flex-col gap-1">
                <Label htmlFor="ds-mapping">Column mapping (JSON)</Label>
                <Textarea
                  id="ds-mapping"
                  rows={6}
                  value={mapping}
                  onChange={(e) => setMapping(e.target.value)}
                  className="font-mono text-xs"
                />
              </div>
            ) : null}

            <div className="flex flex-wrap items-center gap-3">
              <Button type="submit" disabled={upload.isPending}>
                {upload.isPending ? "Uploading…" : "Upload"}
              </Button>
              <label className="flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={trainAfter}
                  onChange={(e) => setTrainAfter(e.target.checked)}
                />
                Train after upload
              </label>
              <NativeSelect value={mode} onChange={(e) => setMode(e.target.value)}>
                <NativeSelectOption value="single">Single model</NativeSelectOption>
                <NativeSelectOption value="best">Best of matrix</NativeSelectOption>
              </NativeSelect>
              {mode === "single" ? (
                <Input className="w-40" value={model} onChange={(e) => setModel(e.target.value)} />
              ) : null}
            </div>
          </form>
        </CardContent>
      </Card>

      {error ? (
        <Alert>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      ) : null}

      {datasets.isLoading ? (
        <PanelSkeleton title="Sources" />
      ) : (
        <Card>
          <CardHeader>
            <CardTitle>Sources</CardTitle>
            <CardDescription>
              Built-in and uploaded datasets, and whether a model exists.
            </CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col gap-2">
            {(datasets.data?.sources ?? []).map((source) => (
              <div
                key={source.name}
                className="flex flex-wrap items-center justify-between gap-3 border-b py-2 last:border-b-0"
              >
                <div className="flex items-center gap-2">
                  <span className="font-medium">{source.name}</span>
                  <Badge variant="secondary">{source.kind}</Badge>
                  {source.trained ? <Badge>trained</Badge> : null}
                </div>
                <div className="flex items-center gap-2">
                  <Button
                    size="sm"
                    variant="outline"
                    disabled={train.isPending}
                    onClick={() => onTrain(source.name)}
                  >
                    Train
                  </Button>
                  {source.kind === "upload" ? (
                    <Button
                      size="sm"
                      variant="outline"
                      disabled={remove.isPending}
                      onClick={() => onDelete(source.name)}
                    >
                      Delete
                    </Button>
                  ) : null}
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
