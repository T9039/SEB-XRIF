import { useState } from "react";
import {
  Button,
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  NativeSelect,
  NativeSelectOption,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@humanity-erp/ui";
import { useLearners, useOptions } from "../api/hooks";
import { PanelMessage, PanelSkeleton } from "./panel-states";

const COLUMNS: { key: string; label: string }[] = [
  { key: "gender", label: "Gender" },
  { key: "StageID", label: "Stage" },
  { key: "Topic", label: "Topic" },
  { key: "raisedhands", label: "Raised hands" },
  { key: "VisITedResources", label: "Visited" },
  { key: "AnnouncementsView", label: "Announcements" },
  { key: "Discussion", label: "Discussion" },
  { key: "Class", label: "Tier" },
];

const PAGE_SIZE = 10;

export function LearnerTable() {
  const [topic, setTopic] = useState("");
  const [tier, setTier] = useState("");
  const [offset, setOffset] = useState(0);

  const { data: optionsData } = useOptions();
  const { data, isLoading, isError } = useLearners({
    limit: PAGE_SIZE,
    offset,
    topic: topic || undefined,
    tier: tier || undefined,
  });

  if (isLoading) return <PanelSkeleton title="Learner records" />;
  if (isError || !data) {
    return <PanelMessage title="Learner records" message="Data unavailable." />;
  }

  const total = data.total;
  const canPrev = offset > 0;
  const canNext = offset + PAGE_SIZE < total;

  const reset = (setter: (value: string) => void) => (value: string) => {
    setter(value);
    setOffset(0);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Learner records</CardTitle>
        <CardDescription>
          {total} records from {data.data_source}
        </CardDescription>
      </CardHeader>
      <CardContent className="flex flex-col gap-4">
        <div className="flex flex-wrap items-end gap-3">
          <label className="flex flex-col gap-1 text-xs text-muted-foreground">
            Topic
            <NativeSelect value={topic} onChange={(event) => reset(setTopic)(event.target.value)}>
              <NativeSelectOption value="">All</NativeSelectOption>
              {(optionsData?.options.Topic ?? []).map((option) => (
                <NativeSelectOption key={option} value={option}>
                  {option}
                </NativeSelectOption>
              ))}
            </NativeSelect>
          </label>
          <label className="flex flex-col gap-1 text-xs text-muted-foreground">
            Tier
            <NativeSelect value={tier} onChange={(event) => reset(setTier)(event.target.value)}>
              <NativeSelectOption value="">All</NativeSelectOption>
              {["L", "M", "H"].map((option) => (
                <NativeSelectOption key={option} value={option}>
                  {option}
                </NativeSelectOption>
              ))}
            </NativeSelect>
          </label>
        </div>

        <Table>
          <TableHeader>
            <TableRow>
              {COLUMNS.map((column) => (
                <TableHead key={column.key}>{column.label}</TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {data.rows.map((row, index) => (
              <TableRow key={offset + index}>
                {COLUMNS.map((column) => (
                  <TableCell key={column.key}>{String(row[column.key] ?? "—")}</TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>

        <div className="flex items-center justify-between">
          <span className="text-xs text-muted-foreground">
            {total === 0
              ? "No records"
              : `${offset + 1}–${Math.min(offset + PAGE_SIZE, total)} of ${total}`}
          </span>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              disabled={!canPrev}
              onClick={() => setOffset(Math.max(0, offset - PAGE_SIZE))}
            >
              Previous
            </Button>
            <Button
              variant="outline"
              size="sm"
              disabled={!canNext}
              onClick={() => setOffset(offset + PAGE_SIZE)}
            >
              Next
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
