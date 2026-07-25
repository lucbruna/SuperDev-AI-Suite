"use client";

import { type HTMLAttributes, type ReactNode } from "react";
import { cn } from "@/utils/cn";

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode;
  header?: ReactNode;
  footer?: ReactNode;
  padding?: "none" | "sm" | "md" | "lg";
  hover?: boolean;
}

const paddingStyles = {
  none: "",
  sm: "p-3",
  md: "p-5",
  lg: "p-7",
};

export function Card({
  children,
  header,
  footer,
  padding = "md",
  hover = false,
  className,
  ...props
}: CardProps) {
  return (
    <div
      className={cn(
        "rounded-xl border border-surface-200 bg-white shadow-sm dark:border-surface-700 dark:bg-surface-900",
        hover &&
          "transition-shadow hover:shadow-md dark:hover:border-surface-600",
        className,
      )}
      {...props}
    >
      {header && (
        <div className="border-b border-surface-200 px-5 py-4 dark:border-surface-700">
          {header}
        </div>
      )}
      <div className={cn(paddingStyles[padding])}>{children}</div>
      {footer && (
        <div className="border-t border-surface-200 px-5 py-4 dark:border-surface-700">
          {footer}
        </div>
      )}
    </div>
  );
}

export function CardHeader({ children, className }: { children: ReactNode; className?: string }) {
  return (
    <div className={cn("flex items-center justify-between", className)}>
      {children}
    </div>
  );
}

export function CardBody({ children, className }: { children: ReactNode; className?: string }) {
  return <div className={cn("space-y-4", className)}>{children}</div>;
}

export function CardFooter({ children, className }: { children: ReactNode; className?: string }) {
  return (
    <div className={cn("flex items-center justify-end gap-3", className)}>
      {children}
    </div>
  );
}
