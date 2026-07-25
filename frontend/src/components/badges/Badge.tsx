"use client";

import { type ReactNode } from "react";
import { cn } from "@/utils/cn";

type BadgeVariant = "default" | "primary" | "success" | "warning" | "danger" | "info";
type BadgeSize = "sm" | "md" | "lg";

interface BadgeProps {
  children: ReactNode;
  variant?: BadgeVariant;
  size?: BadgeSize;
  className?: string;
  dot?: boolean;
  removable?: boolean;
  onRemove?: () => void;
}

const variantStyles: Record<BadgeVariant, string> = {
  default:
    "bg-surface-100 text-surface-700 dark:bg-surface-800 dark:text-surface-300",
  primary:
    "bg-primary-50 text-primary-700 dark:bg-primary-950 dark:text-primary-300",
  success:
    "bg-green-50 text-green-700 dark:bg-green-950 dark:text-green-300",
  warning:
    "bg-amber-50 text-amber-700 dark:bg-amber-950 dark:text-amber-300",
  danger:
    "bg-red-50 text-red-700 dark:bg-red-950 dark:text-red-300",
  info:
    "bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-300",
};

const sizeStyles: Record<BadgeSize, string> = {
  sm: "px-1.5 py-0.5 text-xs",
  md: "px-2.5 py-1 text-xs",
  lg: "px-3 py-1.5 text-sm",
};

const dotColors: Record<BadgeVariant, string> = {
  default: "bg-surface-400",
  primary: "bg-primary-500",
  success: "bg-green-500",
  warning: "bg-amber-500",
  danger: "bg-red-500",
  info: "bg-blue-500",
};

export function Badge({
  children,
  variant = "default",
  size = "md",
  className,
  dot = false,
  removable = false,
  onRemove,
}: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 font-medium rounded-full",
        variantStyles[variant],
        sizeStyles[size],
        className,
      )}
    >
      {dot && <span className={cn("h-1.5 w-1.5 rounded-full", dotColors[variant])} />}
      {children}
      {removable && (
        <button
          type="button"
          onClick={onRemove}
          className="ml-0.5 inline-flex items-center rounded-full p-0.5 hover:bg-black/10 dark:hover:bg-white/10"
          aria-label="Remove"
        >
          <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      )}
    </span>
  );
}
