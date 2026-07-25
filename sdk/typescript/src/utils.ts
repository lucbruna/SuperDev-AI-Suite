/**
 * Retry an async function with exponential backoff.
 *
 * @param fn      - The async function to retry.
 * @param opts    - Retry configuration.
 * @returns The result of `fn`.
 * @throws The last error if all retries fail.
 */
export async function retry<T>(
  fn: () => Promise<T>,
  opts: { maxRetries?: number; delay?: number; backoff?: number } = {},
): Promise<T> {
  const { maxRetries = 3, delay = 1000, backoff = 2 } = opts;
  let lastError: Error | undefined;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (err) {
      lastError = err instanceof Error ? err : new Error(String(err));
      if (attempt < maxRetries) {
        await sleep(delay * backoff ** attempt);
      }
    }
  }
  throw lastError;
}

/** Sleep for `ms` milliseconds. */
function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Truncate a string to `maxLength`, appending `suffix` if truncated.
 *
 * @example
 * ```ts
 * truncate("Hello, World!", 5); // "He..."
 * ```
 */
export function truncate(
  text: string,
  maxLength = 100,
  suffix = "...",
): string {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength - suffix.length) + suffix;
}

/**
 * Convert a string to a URL-safe slug.
 *
 * @example
 * ```ts
 * slugify("Hello World!"); // "hello-world"
 * ```
 */
export function slugify(text: string): string {
  return text
    .toLowerCase()
    .trim()
    .replace(/[^\w\s-]/g, "")
    .replace(/[\s_]+/g, "-")
    .replace(/-+/g, "-")
    .replace(/^-|-$/g, "");
}

/**
 * Format a token count for display (e.g. 1500 → "1.5K").
 */
export function formatTokens(count: number): string {
  if (count >= 1_000_000) return `${(count / 1_000_000).toFixed(1)}M`;
  if (count >= 1_000) return `${(count / 1_000).toFixed(1)}K`;
  return String(count);
}

/**
 * Format a cost amount for display.
 */
export function formatCost(amount: number, currency = "USD"): string {
  if (currency === "USD") return `$${amount.toFixed(4)}`;
  return `${amount.toFixed(4)} ${currency}`;
}

/**
 * Deep-merge two objects, with `override` taking precedence.
 */
export function mergeObjects<T extends Record<string, unknown>>(
  base: T,
  override: Partial<T>,
): T {
  const result = { ...base };
  for (const [key, value] of Object.entries(override)) {
    if (
      key in result &&
      typeof result[key] === "object" &&
      result[key] !== null &&
      typeof value === "object" &&
      value !== null &&
      !Array.isArray(result[key]) &&
      !Array.isArray(value)
    ) {
      (result as Record<string, unknown>)[key] = mergeObjects(
        result[key] as Record<string, unknown>,
        value as Record<string, unknown>,
      );
    } else if (value !== undefined) {
      (result as Record<string, unknown>)[key] = value;
    }
  }
  return result;
}

/**
 * Parse a rate-limit header value into a key-value map.
 *
 * @example
 * ```ts
 * parseRateLimitHeader("limit=100, remaining=42, reset=1700000000");
 * // { limit: 100, remaining: 42, reset: 1700000000 }
 * ```
 */
export function parseRateLimitHeader(header: string): Record<string, number> {
  const result: Record<string, number> = {};
  for (const part of header.split(",")) {
    const trimmed = part.trim();
    const eqIndex = trimmed.indexOf("=");
    if (eqIndex === -1) continue;
    const key = trimmed.slice(0, eqIndex).trim();
    const value = trimmed.slice(eqIndex + 1).trim();
    const num = Number(value);
    if (!Number.isNaN(num)) {
      result[key] = num;
    }
  }
  return result;
}
