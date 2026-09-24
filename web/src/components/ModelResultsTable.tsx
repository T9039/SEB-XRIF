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
import { useResults } from "../api/hooks";
import { PanelMessage, PanelSkeleton } from "./panel-states";
import type { ResultRow } from "../types";

function percent(value: number | null): string {
  return value === null || Number.isNaN(value) ? "—" : `${(value * 100).toFixed(1)}%`;
}

const columns: ColumnDef<ResultRow>[] = [
  {
    accessorKey: "model",
    header: "Model",
    enableSorting: true,
    cell: ({ row }) => <span className="font-medium">{String(row.getValue("model"))}</span>,
  },
  {
    accessorKey: "accuracy",
    header: "Accuracy",
    enableSorting: true,
    cell: ({ row }) => percent(row.getValue("accuracy")),
  },
  {
    accessorKey: "f1_macro",
    header: "Macro F1",
    enableSorting: true,
    cell: ({ row }) => percent(row.getValue("f1_macro")),
  },
  {
    accessorKey: "cv_mean",
    header: "CV macro F1",
    enableSorting: true,
    cell: ({ row }) => percent(row.getValue("cv_mean")),
  },
  {
    accessorKey: "cv_std",
    header: "CV std",
    enableSorting: true,
    cell: ({ row }) => {
      const value = row.getValue("cv_std") as number | null;
      return value === null ? "—" : value.toFixed(4);
    },
  },
  {
    accessorKey: "roc_auc_ovr",
    header: "ROC-AUC",
    enableSorting: true,
    cell: ({ row }) => percent(row.getValue("roc_auc_ovr")),
  },
  {
    accessorKey: "fit_seconds",
    header: "Fit (s)",
    enableSorting: true,
    cell: ({ row }) => {
      const value = row.getValue("fit_seconds") as number | null;
      return value === null ? "—" : value.toFixed(3);
    },
  },
  {
    accessorKey: "status",
    header: "Status",
    enableSorting: true,
    cell: ({ row }) => {
      const status = String(row.getValue("status"));
      return <Badge variant={status === "ok" ? "secondary" : "destructive"}>{status}</Badge>;
    },
  },
];

export function ModelResultsTable() {
  const { data, isLoading, isError } = useResults();

  if (isLoading) return <PanelSkeleton title="Model comparison" />;
  if (isError || !data) {
    return <PanelMessage title="Model comparison" message="No results yet — run `make matrix`." />;
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Model comparison</CardTitle>
        <CardDescription>{data.results.length} models · sortable, searchable</CardDescription>
      </CardHeader>
      <CardContent>
        <DataTable columns={columns} data={data.results} pageSize={10}>
          <DataTable.Toolbar>
            <DataTable.SearchInput placeholder="Search models..." />
          </DataTable.Toolbar>
        </DataTable>
      </CardContent>
    </Card>
  );
}
