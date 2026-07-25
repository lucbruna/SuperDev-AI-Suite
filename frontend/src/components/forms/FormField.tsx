"use client";

import { type ReactNode } from "react";
import { cn } from "@/utils/cn";

interface FormFieldProps {
  label?: string;
  error?: string;
  hint?: string;
  required?: boolean;
  children: ReactNode;
  className?: string;
  labelClassName?: string;
  errorClassName?: string;
}

export function FormField({
  label,
  error,
  hint,
  required = false,
  children,
  className,
  labelClassName,
  errorClassName,
}: FormFieldProps) {
  const fieldId = label?.toLowerCase().replace(/\s+/g, "-");

  return (
    <div className={cn("space-y-1.5", className)}>
      {label && (
        <label
          htmlFor={fieldId}
          className={cn(
            "text-sm font-medium text-surface-700 dark:text-surface-300",
            required &&
              "after:ml-0.5 after:text-red-500 after:content-['*']",
            labelClassName,
          )}
        >
          {label}
        </label>
      )}
      {children}
      {error && (
        <p
          id={`${fieldId}-error`}
          className={cn("text-xs text-red-500", errorClassName)}
          role="alert"
        >
          {error}
        </p>
      )}
      {hint && !error && (
        <p className="text-xs text-surface-500 dark:text-surface-400">
          {hint}
        </p>
      )}
    </div>
  );
}
