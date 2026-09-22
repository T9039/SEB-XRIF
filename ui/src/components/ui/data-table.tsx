import { createContext, useContext, useMemo, useState } from "react";
import {
  flexRender,
  getCoreRowModel,
  getSortedRowModel,
  getPaginationRowModel,
  getFilteredRowModel,
  useReactTable,
  type ColumnDef,
  type SortingState,
  type ColumnFiltersState,
  type RowData,
  type Row,
  type Table,
} from "@tanstack/react-table";
import { ArrowUpDown, ArrowUp, ArrowDown, Search, FileIcon } from "lucide-react";
import {
  Table as TableComponent,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
} from "./table";
import { Input } from "./input";
import { Select, SelectContent, SelectItem, SelectTrigger } from "./select";
import { PaginationBar } from "./pagination-bar";
import { Skeleton } from "./skeleton";
import { InlineEmptyState } from "./inline-empty-state";
import { cn } from "../../lib/utils";

declare module "@tanstack/react-table" {
  interface ColumnMeta<TData extends RowData, TValue> {
    align?: "left" | "right" | "center";
  }
}

interface DataTableContextValue<TData> {
  table: Table<TData>;
}

const DataTableContext = createContext<DataTableContextValue<unknown> | null>(null);

function useDataTableContext<TData>(): DataTableContextValue<TData> {
  const context = useContext(DataTableContext);
  if (!context) {
    throw new Error("DataTable subcomponents must be used within DataTable");
  }
  return context as DataTableContextValue<TData>;
}

interface DataTableProps<TData> {
  columns: ColumnDef<TData, any>[];
  data: TData[];
  pageSize?: number;
  onRowClick?: (row: TData) => void;
  getRowId?: (row: TData) => string;
  isLoading?: boolean;
  loadingRows?: number;
  showSearch?: boolean;
  searchPlaceholder?: string;
  emptyTitle?: string;
  emptyDescription?: string;
  emptyIcon?: React.ComponentType<{ className?: string }>;
  children?: React.ReactNode;
}

function DataTableSkeleton({ columns, rows }: { columns: number; rows: number }) {
  return (
    <div className="rounded-xl border bg-card shadow-xs" role="status">
      <div className="flex gap-4 border-b px-4 py-3 bg-muted/30">
        {Array.from({ length: columns }).map((_, i) => (
          <Skeleton key={i} className="h-4" style={{ flex: i === columns - 1 ? 0.5 : 1 }} />
        ))}
      </div>
      {Array.from({ length: rows }).map((_, i) => (
        <div
          key={i}
          className="flex gap-4 border-b border-border/50 px-4 py-3 last:border-b-0 items-center"
        >
          {Array.from({ length: columns }).map((_, j) => (
            <Skeleton key={j} className="h-4" style={{ flex: j === columns - 1 ? 0.5 : 1 }} />
          ))}
        </div>
      ))}
    </div>
  );
}

function DataTableTable<TData>({
  columns,
  onRowClick,
  emptyTitle,
  emptyDescription,
  emptyIcon = FileIcon,
}: {
  columns: ColumnDef<TData, any>[];
  onRowClick?: (row: TData) => void;
  emptyTitle?: string;
  emptyDescription?: string;
  emptyIcon?: React.ComponentType<{ className?: string }>;
}) {
  const { table } = useDataTableContext<TData>();
  const rows = table.getRowModel().rows;
  const totalPages = table.getPageCount();
  const pagination = table.getState().pagination;

  return (
    <div className="rounded-xl border bg-card shadow-md">
      <TableComponent>
        <TableHeader>
          {table.getHeaderGroups().map((headerGroup) => (
            <TableRow key={headerGroup.id} className="bg-muted/30">
              {headerGroup.headers.map((header) => {
                const canSort = header.column.getCanSort();
                const sortDirection = header.column.getIsSorted();
                return (
                  <TableHead
                    key={header.id}
                    className={cn(
                      canSort && "cursor-pointer select-none",
                      header.column.columnDef.meta?.align === "right" && "text-right",
                    )}
                    onClick={canSort ? header.column.getToggleSortingHandler() : undefined}
                  >
                    <div className="flex items-center gap-1">
                      {flexRender(header.column.columnDef.header, header.getContext())}
                      {canSort && (
                        <span className="text-muted-foreground">
                          {sortDirection === "asc" ? (
                            <ArrowUp className="size-3.5" />
                          ) : sortDirection === "desc" ? (
                            <ArrowDown className="size-3.5" />
                          ) : (
                            <ArrowUpDown className="size-3.5 opacity-50" />
                          )}
                        </span>
                      )}
                    </div>
                  </TableHead>
                );
              })}
            </TableRow>
          ))}
        </TableHeader>
        <TableBody>
          {rows.length === 0 ? (
            <TableRow>
              <TableCell
                colSpan={columns.length}
                className="h-48 text-center text-muted-foreground"
              >
                {emptyTitle ? (
                  <InlineEmptyState
                    icon={emptyIcon}
                    title={emptyTitle}
                    description={emptyDescription}
                  />
                ) : (
                  "No results."
                )}
              </TableCell>
            </TableRow>
          ) : (
            rows.map((row: Row<TData>) => (
              <TableRow
                key={row.id}
                onClick={() => onRowClick?.(row.original)}
                className={cn(onRowClick && "cursor-pointer")}
              >
                {row.getVisibleCells().map((cell) => (
                  <TableCell
                    key={cell.id}
                    className={cn(cell.column.columnDef.meta?.align === "right" && "text-right")}
                  >
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </TableCell>
                ))}
              </TableRow>
            ))
          )}
        </TableBody>
      </TableComponent>
      {totalPages > 1 && (
        <PaginationBar
          currentPage={pagination.pageIndex + 1}
          totalPages={totalPages}
          onPageChange={(page) => table.setPageIndex(page - 1)}
        />
      )}
    </div>
  );
}

function DataTableInternal<TData>({
  columns,
  data,
  pageSize = 10,
  onRowClick,
  getRowId,
  isLoading = false,
  loadingRows = 5,
  showSearch = false,
  searchPlaceholder = "Search...",
  emptyTitle,
  emptyDescription,
  emptyIcon = FileIcon,
  children,
}: DataTableProps<TData>) {
  const [sorting, setSorting] = useState<SortingState>([]);
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [globalFilter, setGlobalFilter] = useState("");
  const [pagination, setPagination] = useState({ pageIndex: 0, pageSize });

  const table = useReactTable({
    data,
    columns,
    state: { sorting, pagination, columnFilters, globalFilter },
    onSortingChange: setSorting,
    onPaginationChange: setPagination,
    onColumnFiltersChange: setColumnFilters,
    onGlobalFilterChange: setGlobalFilter,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getRowId,
  });

  const headerCount = useMemo(
    () => table.getHeaderGroups()[0]?.headers.length ?? columns.length,
    [table, columns.length],
  );

  if (isLoading) {
    return <DataTableSkeleton columns={headerCount} rows={loadingRows} />;
  }

  const contextValue: DataTableContextValue<TData> = { table };

  return (
    <DataTableContext.Provider value={contextValue as DataTableContextValue<unknown>}>
      {children}
      {showSearch && (
        <div className="relative mb-4">
          <Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder={searchPlaceholder}
            value={globalFilter}
            onChange={(e) => setGlobalFilter(e.target.value)}
            className="pl-9"
          />
        </div>
      )}
      <DataTableTable
        columns={columns}
        onRowClick={onRowClick}
        emptyTitle={emptyTitle}
        emptyDescription={emptyDescription}
        emptyIcon={emptyIcon}
      />
    </DataTableContext.Provider>
  );
}

interface DataTableToolbarProps {
  children: React.ReactNode;
  className?: string;
}

function DataTableToolbar({ children, className }: DataTableToolbarProps) {
  return <div className={cn("flex flex-wrap items-center gap-4 mb-4", className)}>{children}</div>;
}

interface DataTableSearchInputProps {
  placeholder?: string;
  className?: string;
}

function DataTableSearchInput({ placeholder = "Search...", className }: DataTableSearchInputProps) {
  const { table } = useDataTableContext();
  const globalFilter = (table.getState().globalFilter as string) ?? "";

  return (
    <div className="relative flex-1 min-w-64">
      <Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
      <Input
        placeholder={placeholder}
        value={globalFilter}
        onChange={(e) => table.setGlobalFilter(e.target.value)}
        className={cn("pl-9", className)}
      />
    </div>
  );
}

interface DataTableFilterGroupProps {
  children: React.ReactNode;
  className?: string;
}

function DataTableFilterGroup({ children, className }: DataTableFilterGroupProps) {
  return <div className={cn("flex items-center gap-4", className)}>{children}</div>;
}

interface DataTableFilterSelectProps {
  columnId: string;
  options: { value: string; label: string }[];
  placeholder?: string;
  className?: string;
  allOption?: { value: string; label: string };
}

function DataTableFilterSelect({
  columnId,
  options,
  placeholder,
  className,
  allOption,
}: DataTableFilterSelectProps) {
  const { table } = useDataTableContext();
  const column = table.getColumn(columnId);
  const filterValue = (column?.getFilterValue() as string) ?? "";

  const handleValueChange = (value: string | null) => {
    if (value === null || value === "" || value === "all") {
      column?.setFilterValue(undefined);
    } else {
      column?.setFilterValue(value);
    }
  };

  const allOptions = allOption ? [allOption, ...options] : options;
  const selectedOption = allOptions.find((opt) => opt.value === (filterValue || "all"));

  return (
    <Select value={filterValue || "all"} onValueChange={handleValueChange}>
      <SelectTrigger size="sm" className={cn("min-w-32", className)}>
        {selectedOption?.label || placeholder || "Select..."}
      </SelectTrigger>
      <SelectContent>
        {allOptions.map((option) => (
          <SelectItem key={option.value} value={option.value}>
            {option.label}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}

export const DataTable = Object.assign(DataTableInternal, {
  Toolbar: DataTableToolbar,
  SearchInput: DataTableSearchInput,
  FilterGroup: DataTableFilterGroup,
  FilterSelect: DataTableFilterSelect,
});

export type {
  DataTableProps,
  DataTableToolbarProps,
  DataTableSearchInputProps,
  DataTableFilterGroupProps,
  DataTableFilterSelectProps,
};
