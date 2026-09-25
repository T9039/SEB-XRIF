import { Badge, Label, NativeSelect, NativeSelectOption } from "@humanity-erp/ui";
import { useSource } from "../lib/source-context";
import { DATA_SOURCES } from "../lib/sources";

/** Persistent data-source selector shown in the dashboard header. */
export function SourceSelector() {
  const { source, sourceId, setSourceId } = useSource();

  return (
    <div className="flex items-center gap-3">
      <Badge variant={source.kind === "xr" ? "default" : "secondary"}>
        {source.kind === "xr" ? "XR" : "LMS"}
      </Badge>
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
          {DATA_SOURCES.map((option) => (
            <NativeSelectOption key={option.id} value={option.id}>
              {option.label}
            </NativeSelectOption>
          ))}
        </NativeSelect>
      </div>
    </div>
  );
}
