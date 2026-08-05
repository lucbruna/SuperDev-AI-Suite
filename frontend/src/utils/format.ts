// ---------------------------------------------------------------------------
// Generic pure formatting helpers (bytes, durations, render estimates, badge
// variants). Kept free of React so every function is trivially unit-testable.
// ---------------------------------------------------------------------------

import type { ProjectRole, ProjectStatus } from "@/types/project";

/** Human-friendly byte size (B / KB / MB). */
export function fmtBytes(n?: number | null): string {
  if (!n) return "0 B";
  if (n >= 1e6) return `${(n / 1e6).toFixed(1)} MB`;
  if (n >= 1e3) return `${(n / 1e3).toFixed(0)} KB`;
  return `${n} B`;
}

/** Compact duration formatter ("30s", "1 min", "2min 30s"). */
export function fmtDuration(seconds: number): string {
  if (seconds < 60) return `${seconds}s`;
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return s === 0 ? `${m} min` : `${m}min ${s}s`;
}

/** Format an estimated render time (e.g. "~1h 30min", "~2 dias"). */
export function fmtEstimate(seconds: number): string {
  if (seconds < 60) return `~${Math.round(seconds)}s`;
  let m = Math.floor(seconds / 60);
  let s = Math.round(seconds % 60);
  // Carry a rounded remainder of 60s into the minutes (119.6s → "~2 min").
  if (s === 60) {
    m += 1;
    s = 0;
  }
  if (m < 60) {
    return s === 0 ? `~${m} min` : `~${m}min ${s}s`;
  }
  const h = Math.floor(m / 60);
  const restM = m % 60;
  if (h < 24) return restM === 0 ? `~${h} hora${h > 1 ? "s" : ""}` : `~${h}h ${restM}min`;
  const d = Math.floor(h / 24);
  const restH = h % 24;
  return restH === 0 ? `~${d} dia${d > 1 ? "s" : ""}` : `~${d}d ${restH}h`;
}

/** Badge variants produced by a status (mirrors the Badge component's set). */
export type StatusVariant =
  | "success"
  | "warning"
  | "danger"
  | "info"
  | "default"
  | "primary";

/**
 * A TS string enum (e.g. `ProjectStatus`) or plain string-literal union
 * mapped to its member *values* union. `${ProjectStatus}` expands to
 * "active" | "archived" | "deleted" (not the member names "ACTIVE"...).
 */
type DomainValues<Domain extends string> = `${Domain}`;

/**
 * Build a domain-specific status/role → Badge variant mapper with
 * compile-time total coverage. Pass the domain type explicitly — a string
 * enum such as `ProjectStatus`/`ProjectRole` or a string-literal union — and
 * TypeScript rejects any map that omits a member or adds a key outside the
 * domain. Without an explicit type argument the domain is inferred from the
 * map keys. Unknown statuses at runtime still fall back to `fallback`
 * (defaults to "default").
 */
export function createStatusVariantMapper<Domain extends string>(
  variants: Record<DomainValues<Domain>, StatusVariant>,
  fallback: StatusVariant = "default",
): (status: string) => StatusVariant {
  return (status) => variants[status as DomainValues<Domain>] ?? fallback;
}

/** Job generation status → Badge variant. */
export const jobStatusVariant = createStatusVariantMapper({
  completed: "success",
  failed: "danger",
  queued: "warning",
  processing: "info",
});

/** Project status → Badge variant. Total ProjectStatus coverage is type-enforced. */
export const projectStatusVariant = createStatusVariantMapper<ProjectStatus>({
  active: "success",
  archived: "warning",
  deleted: "danger",
});

/** Member status → Badge variant. Keep in sync with every member status value. */
export const memberStatusVariant = createStatusVariantMapper({
  active: "success",
  invited: "warning",
  pending: "warning",
});

/** Member/team role → Badge variant. Total ProjectRole coverage is type-enforced. */
export const roleVariant = createStatusVariantMapper<ProjectRole>({
  owner: "primary",
  admin: "info",
  member: "default",
  viewer: "default",
});

/** Dashboard activity type → Badge variant. */
export const activityVariant = createStatusVariantMapper({
  agent: "info",
  workflow: "warning",
  workflow_run: "warning",
  project: "default",
  error: "danger",
  create: "success",
  update: "info",
  delete: "danger",
  execute: "success",
  auth: "default",
});

/** Video Studio backend health → Badge variant. */
export const studioHealthVariant = createStatusVariantMapper({
  checking: "default",
  healthy: "success",
  offline: "danger",
});

/**
 * System service health → Badge variant. Unknown/unhealthy states are
 * dangerous, matching the old inline ternary (healthy → success, degraded →
 * warning, anything else → danger).
 */
export const serviceHealthVariant = createStatusVariantMapper(
  {
    healthy: "success",
    degraded: "warning",
    unhealthy: "danger",
  },
  "danger",
);
