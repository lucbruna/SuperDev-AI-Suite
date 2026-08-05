// ---------------------------------------------------------------------------
// Compile-time type tests for utils/format.ts.
//
// This file is deliberately NOT a `*.test.*` module (vitest never runs it) but
// it IS part of the tsc program (tsconfig includes `src/**`), so the
// `@ts-expect-error` guards below are verified by `npm run typecheck`. If the
// coverage guarantee ever regresses, tsc fails with an "unused directive".
// ---------------------------------------------------------------------------

import { createStatusVariantMapper } from "./format";
import type { ProjectRole, ProjectStatus } from "@/types/project";

// All members of the ProjectStatus enum are covered → must compile.
createStatusVariantMapper<ProjectStatus>({
  active: "success",
  archived: "warning",
  deleted: "danger",
});

// Omitting an enum member must fail to compile.
// @ts-expect-error — every ProjectStatus member must be mapped
createStatusVariantMapper<ProjectStatus>({
  active: "success",
  archived: "warning",
});

// Adding a key outside the domain must fail to compile. The excess-property
// error is reported on the offending key's line, so the directive sits there.
createStatusVariantMapper<ProjectStatus>({
  active: "success",
  archived: "warning",
  deleted: "danger",
  // @ts-expect-error — unknown keys are not part of ProjectStatus
  paused: "warning",
});

// Maps without an explicit domain still infer their keys (current behavior).
createStatusVariantMapper({ ok: "success", bad: "danger" });

// String-literal unions work as domains too.
createStatusVariantMapper<"active" | "invited" | "pending">({
  active: "success",
  invited: "warning",
  pending: "warning",
});

// All four ProjectRole members are covered → must compile.
createStatusVariantMapper<ProjectRole>({
  owner: "primary",
  admin: "info",
  member: "default",
  viewer: "default",
});

// Omitting a ProjectRole member must fail to compile.
// @ts-expect-error — every ProjectRole member must be mapped
createStatusVariantMapper<ProjectRole>({
  owner: "primary",
  admin: "info",
  member: "default",
});
