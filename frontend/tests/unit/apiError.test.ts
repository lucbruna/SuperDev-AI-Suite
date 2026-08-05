import { describe, expect, it } from "vitest";
import { extractErrorMessage } from "@/utils/apiError";

describe("extractErrorMessage", () => {
  it("extracts FastAPI validation detail (array of errors)", () => {
    const e = {
      response: {
        data: {
          detail: [
            {
              loc: ["body", "resolution"],
              msg: "Invalid resolution 1920x1088: aspect ratio 30:17 is not supported",
              type: "value_error",
            },
          ],
        },
      },
    };
    expect(extractErrorMessage(e)).toContain("30:17");
    expect(extractErrorMessage(e)).toContain("1920x1088");
  });

  it("extracts HTTPException detail (string)", () => {
    const e = { response: { data: { detail: "Job nope not found" } } };
    expect(extractErrorMessage(e)).toBe("Job nope not found");
  });

  it("falls back to Error.message", () => {
    expect(extractErrorMessage(new Error("network down"))).toBe("network down");
  });

  it("falls back to the default message for unknown errors", () => {
    expect(extractErrorMessage("garbage")).toBe("Falha na requisição");
    expect(extractErrorMessage("garbage", "boom")).toBe("boom");
  });

  it("returns empty detail strings through the fallback", () => {
    const e = { response: { data: { detail: "" } } };
    expect(extractErrorMessage(e, "fallback")).toBe("fallback");
  });
});
