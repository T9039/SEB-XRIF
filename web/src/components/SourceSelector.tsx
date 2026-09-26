import { useMemo } from "react";
import { Badge, Label, NativeSelect, NativeSelectOption } from "@humanity-erp/ui";
import { useDatasets } from "../api/hooks";
import { useSource } from "../lib/source-context";
import { mergeSources } from "../lib/sources";

/** Persistent data-source selector shown in the dashboard header. */
export function SourceSelector() {
  const { source, sourceId, setSourceId } = useSource();
  const datasets = useDatasets();

  const options = useMemo(() => mergeSources(datasets.data?.sources ?? []), [datasets.data]);

  const kindLabel = source.kind === "xr" ? "XR" : source.kind === "lms" ? "LMS" : "DATA";

  return (
    <div className="flex items-center gap-3">
      <Badge variant={source.kind === "xr" ? "default" : "secondary"}>{kindLabel}</Badge>
      <div className="flex flex-col gap-1">
        <Label htmlFor="data-source" className="text-xs text-muted-foreground">
          Data source
        </Label>
        <NativeSelect
          id="data-source"
          value={sourceId}
          onChange={(event) => setSourceId(event.target.value)}
          className="w-64"
        >
          {options.map((option) => (
            <NativeSelectOption key={option.id} value={option.id}>
              {option.label}
            </NativeSelectOption>
          ))}
        </NativeSelect>
      </div>
    </div>
  );
}
