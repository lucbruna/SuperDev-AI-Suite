"use client";

import { type ReactNode } from "react";

// ---------------------------------------------------------------------------
// Utilitários de seção do Centro de Controle.
// ---------------------------------------------------------------------------

export function ControlSection({
  icon,
  title,
  subtitle,
  action,
  children,
}: {
  icon: string;
  title: string;
  subtitle?: string;
  action?: ReactNode;
  children: ReactNode;
}) {
  return (
    <section className="rounded-xl border border-surface-200 bg-white shadow-sm dark:border-surface-700 dark:bg-surface-900">
      <header className="flex items-center justify-between gap-3 border-b border-surface-100 px-5 py-4 dark:border-surface-800">
        <div className="flex items-center gap-3 min-w-0">
          <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-surface-100 text-base dark:bg-surface-800">
            {icon}
          </span>
          <div className="min-w-0">
            <h3 className="text-sm font-semibold text-surface-900 dark:text-surface-50 truncate">
              {title}
            </h3>
            {subtitle && (
              <p className="text-xs text-surface-500 dark:text-surface-400 truncate">{subtitle}</p>
            )}
          </div>
        </div>
        {action && <div className="shrink-0">{action}</div>}
      </header>
      <div className="p-5">{children}</div>
    </section>
  );
}

export function ActionFeedback({ message }: { message: string | null }) {
  if (!message) return null;
  const ok = message.startsWith("✅");
  return (
    <div
      className={`mt-3 rounded-lg px-3 py-2 text-xs font-medium ${
        ok
          ? "bg-green-50 text-green-700 dark:bg-green-950 dark:text-green-300"
          : "bg-red-50 text-red-700 dark:bg-red-950 dark:text-red-300"
      }`}
    >
      {message}
    </div>
  );
}

// Normaliza retornos que podem vir como { data: [...] } / { success, data } / array
// ou envelopes nomeados ({ tasks }, { scanners }, { builders }, { flags }, ...).
export function unwrapList<T>(value: unknown): T[] {
  if (Array.isArray(value)) return value as T[];
  if (value && typeof value === "object") {
    const obj = value as Record<string, unknown>;
    if (Array.isArray(obj.data)) return obj.data as T[];
    if (Array.isArray(obj.items)) return obj.items as T[];
    if (Array.isArray(obj.results)) return obj.results as T[];
    if (Array.isArray(obj.tasks)) return obj.tasks as T[];
    if (Array.isArray(obj.scanners)) return obj.scanners as T[];
    if (Array.isArray(obj.builders)) return obj.builders as T[];
    if (Array.isArray(obj.flags)) return obj.flags as T[];
  }
  return [];
}

export function unwrapObj<T extends Record<string, unknown>>(value: unknown): T {
  if (value && typeof value === "object") {
    const obj = value as Record<string, unknown>;
    if (obj.data && typeof obj.data === "object") return obj.data as T;
    return obj as T;
  }
  return {} as T;
}

export function errMsg(e: unknown): string {
  if (e instanceof Error) return e.message;
  if (typeof e === "string") return e;
  return "erro desconhecido";
}
