import type { ColumnDef } from "@tanstack/react-table";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  DataTable,
} from "@humanity-erp/ui";
import { useXrLearners } from "../api/hooks";
import { useSource } from "../lib/source-context";
import { PanelMessage, PanelSkeleton } from "./panel-states";

type XrRow = Record<string, string | number>;

const NUMERIC = [
  "events",
  "active_days",
  "distinct_verbs",
  "distinct_objects",
  "responses",
  "events_per_active_day",
];

const VERB_CLASSES = [
  "verb_interaction",
  "verb_progress",
  "verb_assessment",
  "verb_content",
  "verb_disengagement",
  "verb_other",
];

const columns: ColumnDef<XrRow>[] = [
  {
    accessorKey: "learner",
    header: "Learner",
    enableSorting: true,
    cell: ({ row }) => <span className="font-medium">{String(row.getValue("learner"))}</span>,
  },
  ...NUMERIC.map((key): ColumnDef<XrRow> => ({
    accessorKey: key,
    header: key === "events_per_active_day" ? "Events/day" : key.replace(/_/g, " "),
    enableSorting: true,
  })),
  ...VERB_CLASSES.map((key): ColumnDef<XrRow> => ({
    accessorKey: key,
    header: key.replace("verb_", ""),
    enableSorting: true,
  })),
];

/** XR per-learner engagement features for the selected pilot. */
export function XrLearnerTable() {
  const { sourceId } = useSource();
  const { data, isLoading, isError } = useXrLearners(sourceId, 200, 0, true);

  if (isLoading) return <PanelSkeleton title="XR engagement features" />;
  if (isError || !data) {
    return (
      <PanelMessage
        title="XR engagement features"
        message={`Download this pilot with \`make fetch-arete ARGS=${sourceId}\`.`}
      />
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>XR engagement features ({data.pilot})</CardTitle>
        <CardDescription>
          {data.total} learners · validated per-learner engagement from xAPI statements
        </CardDescription>
      </CardHeader>
      <CardContent>
        <DataTable columns={columns} data={data.rows} pageSize={15}>
          <DataTable.Toolbar>
            <DataTable.SearchInput placeholder="Search learners..." />
          </DataTable.Toolbar>
        </DataTable>
      </CardContent>
    </Card>
  );
}
