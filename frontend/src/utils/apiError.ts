/**
 * Extract a human-readable message from a failed HTTP request.
 *
 * Handles FastAPI validation errors (`detail: [{loc, msg, type}]`) and
 * HTTPException bodies (`detail: string`), then falls back to the error's own
 * message. This makes a 422 from the video-studio API show the real reason
 * (e.g. "aspect ratio 30:17 is not supported") instead of a generic
 * "Request failed with status code 422".
 */
export function extractErrorMessage(error: unknown, fallback = "Falha na requisição"): string {
  const data = (error as { response?: { data?: unknown } } | undefined)?.response?.data;
  if (data && typeof data === "object") {
    const detail = (data as { detail?: unknown }).detail;
    if (Array.isArray(detail)) {
      const first = detail[0];
      if (first && typeof first === "object" && typeof (first as { msg?: unknown }).msg === "string") {
        return (first as { msg: string }).msg;
      }
      if (typeof first === "string" && first) return first;
    } else if (typeof detail === "string" && detail) {
      return detail;
    }
  }
  return error instanceof Error && error.message ? error.message : fallback;
}
