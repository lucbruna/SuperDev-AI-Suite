"use client";

import { forwardRef, type SelectHTMLAttributes } from "react";
import { cn } from "@/utils/cn";

interface SelectOption {
  value: string;
  label: string;
  disabled?: boolean;
}

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  error?: string;
  hint?: string;
  options: SelectOption[];
  placeholder?: string;
  containerClassName?: string;
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(
  (
    { label, error, hint, options, placeholder, className, containerClassName, id, ...props },
    ref,
  ) => {
    const selectId = id ?? label?.toLowerCase().replace(/\s+/g, "-");

    return (
      <div className={cn("space-y-1.5", containerClassName)}>
        {label && (
          <label
            htmlFor={selectId}
            className="text-sm font-medium text-surface-700 dark:text-surface-300"
          >
            {label}
          </label>
        )}
        <select
          ref={ref}
          id={selectId}
          className={cn(
            "flex h-10 w-full rounded-lg border bg-white px-3 py-2 text-sm text-surface-900 transition-colors",
            "focus:outline-none focus:ring-2 focus:ring-offset-0",
            "disabled:cursor-not-allowed disabled:bg-surface-50 disabled:text-surface-500",
            "dark:bg-surface-900 dark:text-surface-100",
            error
              ? "border-red-500 focus:ring-red-500 dark:border-red-400"
              : "border-surface-300 focus:ring-primary-500 dark:border-surface-600 dark:focus:ring-primary-400",
            className,
          )}
          aria-invalid={!!error}
          {...props}
        >
          {placeholder && (
            <option value="" disabled>
              {placeholder}
            </option>
          )}
          {options.map((option) => (
            <option key={option.value} value={option.value} disabled={option.disabled}>
              {option.label}
            </option>
          ))}
        </select>
        {error && (
          <p className="text-xs text-red-500" role="alert">
            {error}
          </p>
        )}
        {hint && !error && (
          <p className="text-xs text-surface-500 dark:text-surface-400">{hint}</p>
        )}
      </div>
    );
  },
);

Select.displayName = "Select";
