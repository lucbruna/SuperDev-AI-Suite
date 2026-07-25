"use client";

import { type ReactNode } from "react";
import { cn } from "@/utils/cn";

interface ListItem<T> {
  id: string;
  data: T;
}

interface ListProps<T> {
  items: ListItem<T>[];
  renderItem: (item: T, index: number) => ReactNode;
  keyExtractor?: (item: ListItem<T>) => string;
  emptyState?: ReactNode;
  loading?: boolean;
  loadingSkeleton?: ReactNode;
  className?: string;
  itemClassName?: string;
  bordered?: boolean;
  divided?: boolean;
}

export function List<T>({
  items,
  renderItem,
  emptyState,
  loading = false,
  loadingSkeleton,
  className,
  itemClassName,
  bordered = false,
  divided = false,
}: ListProps<T>) {
  if (loading) {
    return (
      <div className={cn("space-y-2", className)}>
        {loadingSkeleton ?? (
          <>
            {Array.from({ length: 3 }).map((_, i) => (
              <div
                key={i}
                className="h-12 animate-pulse rounded-lg bg-surface-100 dark:bg-surface-800"
              />
            ))}
          </>
        )}
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <div className={cn("py-8", className)}>
        {emptyState ?? (
          <p className="text-center text-sm text-surface-500 dark:text-surface-400">
            No items to display
          </p>
        )}
      </div>
    );
  }

  return (
    <ul
      className={cn(
        bordered && "rounded-lg border border-surface-200 dark:border-surface-700",
        className,
      )}
    >
      {items.map((item, index) => (
        <li
          key={item.id}
          className={cn(
            divided && index > 0 && "border-t border-surface-200 dark:border-surface-700",
            itemClassName,
          )}
        >
          {renderItem(item.data, index)}
        </li>
      ))}
    </ul>
  );
}
