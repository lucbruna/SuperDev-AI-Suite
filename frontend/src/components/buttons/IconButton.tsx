"use client";

import { forwardRef, type ButtonHTMLAttributes, type ReactNode } from "react";
import { cn } from "@/utils/cn";

type IconButtonVariant = "primary" | "secondary" | "ghost" | "danger";
type IconButtonSize = "sm" | "md" | "lg";

interface IconButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: IconButtonVariant;
  size?: IconButtonSize;
  icon: ReactNode;
  isLoading?: boolean;
  label: string;
}

const variantStyles: Record<IconButtonVariant, string> = {
  primary:
    "bg-primary-600 text-white hover:bg-primary-700 focus-visible:ring-primary-500 disabled:bg-primary-400",
  secondary:
    "bg-surface-100 text-surface-900 hover:bg-surface-200 focus-visible:ring-surface-500 dark:bg-surface-800 dark:text-surface-100 dark:hover:bg-surface-700",
  ghost:
    "bg-transparent text-surface-600 hover:bg-surface-100 focus-visible:ring-surface-500 dark:text-surface-400 dark:hover:bg-surface-800",
  danger:
    "bg-red-600 text-white hover:bg-red-700 focus-visible:ring-red-500 disabled:bg-red-400",
};

const sizeStyles: Record<IconButtonSize, string> = {
  sm: "h-8 w-8",
  md: "h-10 w-10",
  lg: "h-12 w-12",
};

export const IconButton = forwardRef<HTMLButtonElement, IconButtonProps>(
  (
    {
      variant = "ghost",
      size = "md",
      icon,
      isLoading = false,
      label,
      className,
      disabled,
      ...props
    },
    ref,
  ) => {
    return (
      <button
        ref={ref}
        aria-label={label}
        title={label}
        className={cn(
          "inline-flex items-center justify-center rounded-lg transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50",
          variantStyles[variant],
          sizeStyles[size],
          className,
        )}
        disabled={disabled || isLoading}
        {...props}
      >
        {isLoading ? (
          <svg
            className="h-4 w-4 animate-spin"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
            />
          </svg>
        ) : (
          icon
        )}
      </button>
    );
  },
);

IconButton.displayName = "IconButton";
