import { describe, expect, it } from "vitest";
import {
  activityVariant,
  createStatusVariantMapper,
  fmtBytes,
  fmtDuration,
  fmtEstimate,
  jobStatusVariant,
  memberStatusVariant,
  projectStatusVariant,
  roleVariant,
  serviceHealthVariant,
  studioHealthVariant,
} from "@/utils/format";

describe("fmtBytes", () => {
  it("handles zero, null and undefined as 0 B", () => {
    expect(fmtBytes(0)).toBe("0 B");
    expect(fmtBytes(null)).toBe("0 B");
    expect(fmtBytes(undefined)).toBe("0 B");
  });

  it("formats byte counts", () => {
    expect(fmtBytes(512)).toBe("512 B");
    expect(fmtBytes(999)).toBe("999 B");
  });

  it("formats kilobytes with a >= boundary at 1 KB", () => {
    expect(fmtBytes(1000)).toBe("1 KB");
    expect(fmtBytes(1500)).toBe("2 KB");
  });

  it("formats megabytes with a >= boundary at 1 MB", () => {
    expect(fmtBytes(1_000_000)).toBe("1.0 MB");
    expect(fmtBytes(1_000_001)).toBe("1.0 MB");
    expect(fmtBytes(2_500_000)).toBe("2.5 MB");
    expect(fmtBytes(1_048_576)).toBe("1.0 MB");
  });
});

describe("createStatusVariantMapper", () => {
  it("returns the variant for known statuses", () => {
    const mapper = createStatusVariantMapper({ ok: "success", bad: "danger" });
    expect(mapper("ok")).toBe("success");
    expect(mapper("bad")).toBe("danger");
  });

  it("defaults unknown statuses to default", () => {
    const mapper = createStatusVariantMapper({ ok: "success" });
    expect(mapper("unknown")).toBe("default");
    expect(mapper("")).toBe("default");
  });

  it("honors a custom fallback", () => {
    const mapper = createStatusVariantMapper({ ok: "success", bad: "danger" }, "warning");
    expect(mapper("unknown")).toBe("warning");
    expect(mapper("ok")).toBe("success");
  });
});

describe("jobStatusVariant", () => {
  it("maps known job statuses", () => {
    expect(jobStatusVariant("completed")).toBe("success");
    expect(jobStatusVariant("failed")).toBe("danger");
    expect(jobStatusVariant("queued")).toBe("warning");
    expect(jobStatusVariant("processing")).toBe("info");
  });

  it("falls back to default for unknown statuses", () => {
    expect(jobStatusVariant("done")).toBe("default");
    expect(jobStatusVariant("")).toBe("default");
    expect(jobStatusVariant("bogus")).toBe("default");
  });
});

describe("projectStatusVariant", () => {
  it("maps project statuses to badge variants", () => {
    expect(projectStatusVariant("active")).toBe("success");
    expect(projectStatusVariant("archived")).toBe("warning");
    expect(projectStatusVariant("deleted")).toBe("danger");
  });

  it("falls back to default for unknown project statuses", () => {
    expect(projectStatusVariant("unknown")).toBe("default");
  });
});

describe("memberStatusVariant", () => {
  it("maps member statuses to badge variants", () => {
    expect(memberStatusVariant("active")).toBe("success");
    expect(memberStatusVariant("invited")).toBe("warning");
    expect(memberStatusVariant("pending")).toBe("warning");
  });

  it("falls back to default for unknown member statuses", () => {
    expect(memberStatusVariant("banned")).toBe("default");
  });
});

describe("roleVariant", () => {
  it("maps every ProjectRole member to a badge variant", () => {
    expect(roleVariant("owner")).toBe("primary");
    expect(roleVariant("admin")).toBe("info");
    expect(roleVariant("member")).toBe("default");
    expect(roleVariant("viewer")).toBe("default");
  });

  it("falls back to default for unknown roles", () => {
    expect(roleVariant("superadmin")).toBe("default");
    expect(roleVariant("")).toBe("default");
  });
});

describe("activityVariant", () => {
  it("maps dashboard activity types to badge variants", () => {
    expect(activityVariant("agent")).toBe("info");
    expect(activityVariant("workflow")).toBe("warning");
    expect(activityVariant("workflow_run")).toBe("warning");
    expect(activityVariant("project")).toBe("default");
    expect(activityVariant("error")).toBe("danger");
    expect(activityVariant("create")).toBe("success");
    expect(activityVariant("update")).toBe("info");
    expect(activityVariant("delete")).toBe("danger");
    expect(activityVariant("execute")).toBe("success");
    expect(activityVariant("auth")).toBe("default");
  });

  it("falls back to default for unknown activity types", () => {
    expect(activityVariant("unknown")).toBe("default");
  });
});

describe("studioHealthVariant", () => {
  it("maps Video Studio backend health states", () => {
    expect(studioHealthVariant("checking")).toBe("default");
    expect(studioHealthVariant("healthy")).toBe("success");
    expect(studioHealthVariant("offline")).toBe("danger");
  });

  it("falls back to default for unknown states", () => {
    expect(studioHealthVariant("bogus")).toBe("default");
  });
});

describe("serviceHealthVariant", () => {
  it("maps system health states with a danger fallback", () => {
    expect(serviceHealthVariant("healthy")).toBe("success");
    expect(serviceHealthVariant("degraded")).toBe("warning");
    expect(serviceHealthVariant("unhealthy")).toBe("danger");
  });

  it("treats unknown health states as danger (matching the old ternary)", () => {
    expect(serviceHealthVariant("")).toBe("danger");
    expect(serviceHealthVariant("unknown")).toBe("danger");
  });
});

describe("fmtDuration", () => {
  it("formats sub-minute durations", () => {
    expect(fmtDuration(10)).toBe("10s");
    expect(fmtDuration(59)).toBe("59s");
  });

  it("formats minute+second durations", () => {
    expect(fmtDuration(60)).toBe("1 min");
    expect(fmtDuration(90)).toBe("1min 30s");
    expect(fmtDuration(600)).toBe("10 min");
  });
});

describe("fmtEstimate", () => {
  it("formats seconds", () => {
    expect(fmtEstimate(30)).toBe("~30s");
    expect(fmtEstimate(45.5)).toBe("~46s");
  });

  it("formats minutes", () => {
    expect(fmtEstimate(60)).toBe("~1 min");
    expect(fmtEstimate(90)).toBe("~1min 30s");
    expect(fmtEstimate(600)).toBe("~10 min");
  });

  it("carries a rounded 60s remainder into the minutes", () => {
    expect(fmtEstimate(119.6)).toBe("~2 min");
    expect(fmtEstimate(3599.6)).toBe("~1 hora");
  });

  it("formats hours and days", () => {
    expect(fmtEstimate(3600)).toBe("~1 hora");
    expect(fmtEstimate(5400)).toBe("~1h 30min");
    expect(fmtEstimate(7200)).toBe("~2 horas");
    expect(fmtEstimate(86400)).toBe("~1 dia");
    expect(fmtEstimate(90000)).toBe("~1d 1h");
  });
});
