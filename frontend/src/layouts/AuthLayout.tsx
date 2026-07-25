"use client";

import { type ReactNode } from "react";
import Link from "next/link";

interface AuthLayoutProps {
  children: ReactNode;
  title: string;
  subtitle?: string;
}

export function AuthLayout({ children, title, subtitle }: AuthLayoutProps) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-surface-50 px-4 py-12 dark:bg-surface-950">
      <div className="w-full max-w-md">
        <div className="mb-8 text-center">
          <Link
            href="/"
            className="text-2xl font-bold text-primary-600 dark:text-primary-400"
          >
            SuperDev
          </Link>
          <h1 className="mt-6 text-3xl font-bold tracking-tight text-surface-900 dark:text-surface-50">
            {title}
          </h1>
          {subtitle && (
            <p className="mt-2 text-sm text-surface-500 dark:text-surface-400">
              {subtitle}
            </p>
          )}
        </div>

        <div className="rounded-xl border bg-white p-8 shadow-lg dark:bg-surface-900 dark:border-surface-700">
          {children}
        </div>
      </div>
    </div>
  );
}
