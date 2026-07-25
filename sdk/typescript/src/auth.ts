import { AuthenticationError } from "./errors";

/** Stores a token pair with expiry metadata. */
interface TokenPair {
  accessToken: string;
  refreshToken: string;
  expiresAt: number; // Unix ms
  tokenType: string;
}

/**
 * Manages authentication state — API keys and OAuth-style token pairs.
 *
 * @example
 * ```ts
 * const auth = new AuthManager({ apiKey: "sk-..." });
 * const headers = auth.getHeaders();
 * ```
 */
export class AuthManager {
  private apiKey: string | null;
  private tokenPair: TokenPair | null = null;

  constructor(opts: { apiKey?: string; baseUrl?: string } = {}) {
    this.apiKey = opts.apiKey ?? null;
  }

  /** Build the Authorization and Content-Type headers for a request. */
  getHeaders(): Record<string, string> {
    if (this.apiKey) {
      return {
        Authorization: `Bearer ${this.apiKey}`,
        "Content-Type": "application/json",
      };
    }
    if (this.tokenPair && !this.isExpired) {
      return {
        Authorization: `${this.tokenPair.tokenType} ${this.tokenPair.accessToken}`,
        "Content-Type": "application/json",
      };
    }
    throw new AuthenticationError(
      "No valid credentials available. Login first or provide an API key.",
    );
  }

  /** Store a token pair received from the login endpoint. */
  setTokens(
    accessToken: string,
    refreshToken: string,
    expiresIn: number,
  ): void {
    this.tokenPair = {
      accessToken,
      refreshToken,
      expiresAt: Date.now() + expiresIn * 1000,
      tokenType: "Bearer",
    };
  }

  /** Clear all stored tokens. */
  clearTokens(): void {
    this.tokenPair = null;
  }

  /** Whether the current credentials are valid. */
  get isAuthenticated(): boolean {
    if (this.apiKey) return true;
    return this.tokenPair !== null && !this.isExpired;
  }

  /** The current access token, or null if not authenticated. */
  get accessToken(): string | null {
    if (this.apiKey) return this.apiKey;
    if (this.tokenPair && !this.isExpired) return this.tokenPair.accessToken;
    return null;
  }

  private get isExpired(): boolean {
    if (!this.tokenPair) return false;
    return Date.now() >= this.tokenPair.expiresAt;
  }
}
