import {
  Children,
  isValidElement,
  type ReactElement,
  type ReactNode,
} from "react";
import { cn } from "@/utils/cn";

export { Card, CardBody, CardFooter } from "../cards/Card";
export { Badge } from "../badges/Badge";
export { Button } from "../buttons/Button";
export { Input } from "../inputs/Input";
export { Select } from "../inputs/Select";
export { StatCard } from "../cards/StatCard";
export { Modal } from "../modals/Modal";
export { IconButton } from "../buttons/IconButton";

// Compatibility layer for the innovation dashboard pages: a stable
// "@/components/ui" surface with CardHeader/Table/Tabs/Tab primitives
// matching the API those pages were written against.

export function CardHeader({
  title,
  subtitle,
  className,
}: {
  title?: ReactNode;
  subtitle?: ReactNode;
  className?: string;
}) {
  return (
    <div className={cn("space-y-1", className)}>
      <h3 className="text-lg font-semibold text-surface-900 dark:text-surface-100">
        {title}
      </h3>
      {subtitle ? (
        <p className="text-sm text-surface-500 dark:text-surface-400">
          {subtitle}
        </p>
      ) : null}
    </div>
  );
}

export function Table({
  children,
  className,
}: {
  children?: ReactNode;
  className?: string;
}) {
  return (
    <div className="overflow-x-auto">
      <table className={cn("w-full text-sm", className)}>{children}</table>
    </div>
  );
}

export function Tabs({
  active,
  onChange,
  children,
  className,
}: {
  active?: string;
  onChange?: (id: string) => void;
  children?: ReactNode;
  className?: string;
}) {
  const tabs = Children.toArray(children).filter(isValidElement) as ReactElement<{
    id?: string;
    label?: ReactNode;
  }>[];
  return (
    <div
      role="tablist"
      className={cn("flex gap-1 border-b border-surface-200", className)}
    >
      {tabs.map((tab) => {
        const id = tab.props.id ?? "";
        const isActive = id === active;
        return (
          <button
            key={id}
            type="button"
            role="tab"
            aria-selected={isActive}
            onClick={() => onChange?.(id)}
            className={cn(
              "border-b-2 px-4 py-2 text-sm font-medium transition-colors",
              isActive
                ? "border-primary-500 text-primary-600"
                : "border-transparent text-surface-500 hover:text-surface-700",
            )}
          >
            {tab.props.label}
          </button>
        );
      })}
    </div>
  );
}

export function Tab(_props: { id?: string; label?: ReactNode }) {
  return null;
}

export function Grid({
  cols = 3,
  gap = 4,
  children,
  className,
}: {
  cols?: number;
  gap?: number;
  children?: ReactNode;
  className?: string;
}) {
  return (
    <div
      className={cn("grid", className)}
      style={{
        gridTemplateColumns: `repeat(${cols}, minmax(0, 1fr))`,
        gap: `${gap * 0.25}rem`,
      }}
    >
      {children}
    </div>
  );
}

const textSizes = {
  sm: "text-sm",
  base: "text-base",
  md: "text-base",
  lg: "text-lg",
  xl: "text-xl",
} as const;

export function Text({
  children,
  className,
  size,
}: {
  children?: ReactNode;
  className?: string;
  size?: keyof typeof textSizes;
}) {
  return (
    <p className={cn(size ? textSizes[size] : "text-sm", className)}>
      {children}
    </p>
  );
}
