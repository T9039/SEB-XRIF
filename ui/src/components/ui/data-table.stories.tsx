import type { Meta, StoryObj } from "@storybook/react";
import { fn } from "storybook/test";
import { Badge } from "./badge";
import { DataTable } from "./data-table";
import { CheckCircle2, XCircle, Inbox } from "lucide-react";
import type { ColumnDef } from "@tanstack/react-table";

interface User {
  id: number;
  name: string;
  email: string;
  role: string;
  status: "Active" | "Inactive";
  joined: string;
}

const data: User[] = [
  {
    id: 1,
    name: "Alice Johnson",
    email: "alice@example.com",
    role: "Admin",
    status: "Active",
    joined: "2024-01-15",
  },
  {
    id: 2,
    name: "Bob Smith",
    email: "bob@example.com",
    role: "Editor",
    status: "Active",
    joined: "2024-03-22",
  },
  {
    id: 3,
    name: "Carol White",
    email: "carol@example.com",
    role: "Viewer",
    status: "Inactive",
    joined: "2024-06-10",
  },
  {
    id: 4,
    name: "Dan Brown",
    email: "dan@example.com",
    role: "Editor",
    status: "Active",
    joined: "2024-08-05",
  },
  {
    id: 5,
    name: "Eve Davis",
    email: "eve@example.com",
    role: "Admin",
    status: "Active",
    joined: "2024-09-18",
  },
  {
    id: 6,
    name: "Frank Miller",
    email: "frank@example.com",
    role: "Viewer",
    status: "Inactive",
    joined: "2025-02-01",
  },
  {
    id: 7,
    name: "Grace Lee",
    email: "grace@example.com",
    role: "Editor",
    status: "Active",
    joined: "2025-03-14",
  },
  {
    id: 8,
    name: "Hank Wilson",
    email: "hank@example.com",
    role: "Viewer",
    status: "Active",
    joined: "2025-05-20",
  },
];

const columns: ColumnDef<User>[] = [
  { accessorKey: "name", header: "Name", enableSorting: true },
  { accessorKey: "email", header: "Email", enableSorting: true },
  { accessorKey: "role", header: "Role", enableSorting: true },
  {
    accessorKey: "status",
    header: "Status",
    enableSorting: true,
    cell: ({ row }) => {
      const status = row.getValue("status") as string;
      return (
        <Badge variant={status === "Active" ? "default" : "destructive"}>
          {status === "Active" ? (
            <CheckCircle2 className="size-3" />
          ) : (
            <XCircle className="size-3" />
          )}
          {status}
        </Badge>
      );
    },
  },
  {
    accessorKey: "joined",
    header: "Joined",
    enableSorting: true,
    meta: { align: "right" },
    cell: ({ row }) => <span className="tabular-nums">{row.getValue("joined")}</span>,
  },
];

const meta = {
  title: "UI/DataTable",
  component: DataTable<User>,
  parameters: { layout: "padded" },
  tags: ["autodocs"],
  args: { columns, data },
} satisfies Meta<typeof DataTable<User>>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};

export const WithPagination: Story = {
  args: { pageSize: 3 },
};

export const WithSearch: Story = {
  args: { showSearch: true, searchPlaceholder: "Search users..." },
};

export const WithRowClick: Story = {
  args: { onRowClick: fn() },
};

export const Loading: Story = {
  args: { data: [], isLoading: true, loadingRows: 5 },
};

export const Empty: Story = {
  args: { data: [] },
};

export const EmptyCustom: Story = {
  args: {
    data: [],
    emptyIcon: Inbox,
    emptyTitle: "No users found",
    emptyDescription: "Try adjusting your search or filter criteria.",
  },
};

export const WithComposedToolbar: Story = {
  render: () => (
    <DataTable columns={columns} data={data}>
      <DataTable.Toolbar>
        <DataTable.SearchInput placeholder="Search users..." />
        <DataTable.FilterGroup>
          <DataTable.FilterSelect
            columnId="status"
            placeholder="Status"
            allOption={{ value: "all", label: "All statuses" }}
            options={[
              { value: "Active", label: "Active" },
              { value: "Inactive", label: "Inactive" },
            ]}
          />
          <DataTable.FilterSelect
            columnId="role"
            placeholder="Role"
            allOption={{ value: "all", label: "All roles" }}
            options={[
              { value: "Admin", label: "Admin" },
              { value: "Editor", label: "Editor" },
              { value: "Viewer", label: "Viewer" },
            ]}
          />
        </DataTable.FilterGroup>
      </DataTable.Toolbar>
    </DataTable>
  ),
};
