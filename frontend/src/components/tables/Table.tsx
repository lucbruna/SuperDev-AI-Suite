"use client";

import { type ReactNode, useMemo, useState } from "react";
import { cn } from "@/utils/cn";

interface Column<T> {
  key: string;
  header: string;
  sortable?: boolean;
  render: (item: T) => ReactNode;
  className?: string;
}

interface TableProps<T> {
  columns: Column<T>[];
  data: T[];
  keyExtractor: (item: T) => string;
  page?: number;
  totalPages?: number;
  totalItems?: number;
  onPageChange?: (page: number) => void;
  loading?: boolean;
  emptyState?: ReactNode;
  className?: string;
  onRowClick?: (item: T) => void;
}

export function Table<T>({
  columns,
  data,
  keyExtractor,
  page = 1,
  totalPages = 1,
  totalItems,
  onPageChange,
  loading = false,
  emptyState,
  className,
  onRowClick,
}: TableProps<T>) {
  const [sortKey, setSortKey] = useState<string | null>(null);
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("asc");

  const sortedData = useMemo(() => {
    if (!sortKey) return data;
    return [...data].sort((a, b) => {
      const aVal = (a as Record<string, unknown>)[sortKey] as string;
      const bVal = (b as Record<string, unknown>)[sortKey] as string;
      if (aVal < bVal) return sortOrder === "asc" ? -1 : 1;
      if (aVal > bVal) return sortOrder === "asc" ? 1 : -1;
      return 0;
    });
  }, [data, sortKey, sortOrder]);

  const handleSort = (key: string) => {
    if (sortKey === key) {
      setSortOrder(sortOrder === "asc" ? "desc" : "asc");
    } else {
      setSortKey(key);
      setSortOrder("asc");
    }
  };

  if (loading) {
    return (
      <div className={cn("overflow-hidden rounded-xl border border-surface-200 dark:border-surface-700", className)}>
        <table className="min-w-full divide-y divide-surface-200 dark:divide-surface-700">
          <thead className="bg-surface-50 dark:bg-surface-800">
            <tr>
              {columns.map((col) => (
                <th
                  key={col.key}
                  className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-surface-500 dark:text-surface-400"
                >
                  {col.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-surface-200 dark:divide-surface-700">
            {Array.from({ length: 5 }).map((_, i) => (
              <tr key={i}>
                {columns.map((col) => (
                  <td key={col.key} className="px-4 py-3">
                    <div className="h-4 animate-pulse rounded bg-surface-200 dark:bg-surface-700" />
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  }

  if (data.length === 0) {
    return (
      <div className={cn("py-12 text-center", className)}>
        {emptyState ?? (
          <p className="text-sm text-surface-500 dark:text-surface-400">
            No data to display
          </p>
        )}
      </div>
    );
  }

  return (
    <div className={cn("space-y-4", className)}>
      <div className="overflow-hidden rounded-xl border border-surface-200 dark:border-surface-700">
        <table className="min-w-full divide-y divide-surface-200 dark:divide-surface-700">
          <thead className="bg-surface-50 dark:bg-surface-800">
            <tr>
              {columns.map((col) => (
                <th
                  key={col.key}
                  className={cn(
                    "px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-surface-500 dark:text-surface-400",
                    col.sortable && "cursor-pointer select-none hover:text-surface-700 dark:hover:text-surface-200",
                    col.className,
                  )}
                  onClick={() => col.sortable && handleSort(col.key)}
                >
                  <div className="flex items-center gap-1">
                    {col.header}
                    {col.sortable && sortKey === col.key && (
                      <span>{sortOrder === "asc" ? "↑" : "↓"}</span>
                    )}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-surface-200 bg-white dark:divide-surface-700 dark:bg-surface-900">
            {sortedData.map((item) => (
              <tr
                key={keyExtractor(item)}
                className={cn(
                  "transition-colors",
                  onRowClick && "cursor-pointer hover:bg-surface-50 dark:hover:bg-surface-800",
                )}
                onClick={() => onRowClick?.(item)}
              >
                {columns.map((col) => (
                  <td
                    key={col.key}
                    className={cn("whitespace-nowrap px-4 py-3 text-sm", col.className)}
                  >
                    {col.render(item)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {totalPages > 1 && onPageChange && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-surface-500 dark:text-surface-400">
            {totalItems ? `Total: ${totalItems} items` : ""}
          </p>
          <div className="flex items-center gap-2">
            <button
              onClick={() => onPageChange(page - 1)}
              disabled={page <= 1}
              className="rounded-lg border border-surface-300 px-3 py-1 text-sm disabled:opacity-50 dark:border-surface-600"
            >
              Previous
            </button>
            <span className="text-sm text-surface-600 dark:text-surface-400">
              {page} / {totalPages}
            </span>
            <button
              onClick={() => onPageChange(page + 1)}
              disabled={page >= totalPages}
              className="rounded-lg border border-surface-300 px-3 py-1 text-sm disabled:opacity-50 dark:border-surface-600"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
