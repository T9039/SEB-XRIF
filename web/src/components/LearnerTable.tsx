import type { ColumnDef } from "@tanstack/react-table";
import {
  Badge,
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  DataTable,
} from "@humanity-erp/ui";
import { useLearners, useOptions } from "../api/hooks";
import { PanelMessage, PanelSkeleton } from "./panel-states";

type LearnerRow = Record<string, string | number>;

function TierBadge({ tier }: { tier: string }) {
  const variant = tier === "H" ? "default" : tier === "M" ? "secondary" : "outline";
  return <Badge variant={variant}>{tier}</Badge>;
}

const columns: ColumnDef<LearnerRow>[] = [
  { accessorKey: "gender", header: "Gender", enableSorting: true },
  { accessorKey: "StageID", header: "Stage", enableSorting: true },
  { accessorKey: "Topic", header: "Topic", enableSorting: true, filterFn: "equals" },
  { accessorKey: "raisedhands", header: "Raised hands", enableSorting: true },
  { accessorKey: "VisITedResources", header: "Visited", enableSorting: true },
  { accessorKey: "AnnouncementsView", header: "Announcements", enableSorting: true },
  { accessorKey: "Discussion", header: "Discussion", enableSorting: true },
  {
    accessorKey: "Class",
    header: "Tier",
    enableSorting: true,
    filterFn: "equals",
    cell: ({ row }) => <TierBadge tier={String(row.getValue("Class"))} />,
  },
];

export function LearnerTable() {
  const { data: optionsData } = useOptions();
  const { data, isLoading, isError } = useLearners({ limit: 1000, offset: 0 });

  if (isLoading) return <PanelSkeleton title="Learner records" />;
  if (isError || !data) {
    return <PanelMessage title="Learner records" message="Data unavailable." />;
  }

  const topicOptions = (optionsData?.options.Topic ?? []).map((topic) => ({
    value: topic,
    label: topic,
  }));
  const tierOptions = ["L", "M", "H"].map((tier) => ({ value: tier, label: tier }));

  return (
    <Card>
      <CardHeader>
        <CardTitle>Learner records</CardTitle>
        <CardDescription>
          {data.total} records from {data.data_source} · sortable and filterable
        </CardDescription>
      </CardHeader>
      <CardContent>
        <DataTable columns={columns} data={data.rows} pageSize={10}>
          <DataTable.Toolbar>
            <DataTable.SearchInput placeholder="Search learners..." />
            <DataTable.FilterGroup>
              <DataTable.FilterSelect
                columnId="Topic"
                options={topicOptions}
                allOption={{ value: "all", label: "All topics" }}
                placeholder="Topic"
              />
              <DataTable.FilterSelect
                columnId="Class"
                options={tierOptions}
                allOption={{ value: "all", label: "All tiers" }}
                placeholder="Tier"
              />
            </DataTable.FilterGroup>
          </DataTable.Toolbar>
        </DataTable>
      </CardContent>
    </Card>
  );
}
