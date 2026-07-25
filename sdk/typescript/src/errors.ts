/** Base error class for all SuperDev SDK errors. */
export class SuperDevError extends Error {
  readonly statusCode: number;
  readonly details: Record<string, unknown>;

  constructor(
    message = "An error occurred",
    statusCode = 0,
    details: Record<string, unknown> = {},
  ) {
    super(message);
    this.name = "SuperDevError";
    this.statusCode = statusCode;
    this.details = details;
  }
}

/** Raised when authentication fails (401). */
export class AuthenticationError extends SuperDevError {
  constructor(
    message = "Authentication failed",
    details: Record<string, unknown> = {},
  ) {
    super(message, 401, details);
    this.name = "AuthenticationError";
  }
}

/** Raised when authorization is denied (403). */
export class AuthorizationError extends SuperDevError {
  constructor(
    message = "Authorization denied",
    details: Record<string, unknown> = {},
  ) {
    super(message, 403, details);
    this.name = "AuthorizationError";
  }
}

/** Raised when a resource is not found (404). */
export class NotFoundError extends SuperDevError {
  constructor(
    message = "Resource not found",
    details: Record<string, unknown> = {},
  ) {
    super(message, 404, details);
    this.name = "NotFoundError";
  }
}

/** Raised when request validation fails (422). */
export class ValidationError extends SuperDevError {
  constructor(
    message = "Validation error",
    details: Record<string, unknown> = {},
  ) {
    super(message, 422, details);
    this.name = "ValidationError";
  }
}

/** Raised when rate limit is exceeded (429). */
export class RateLimitError extends SuperDevError {
  readonly retryAfter: number | null;

  constructor(
    message = "Rate limit exceeded",
    retryAfter: number | null = null,
    details: Record<string, unknown> = {},
  ) {
    super(message, 429, details);
    this.name = "RateLimitError";
    this.retryAfter = retryAfter;
  }
}

/** Raised when the server returns a 5xx error. */
export class ServerError extends SuperDevError {
  constructor(
    message = "Server error",
    details: Record<string, unknown> = {},
  ) {
    super(message, 500, details);
    this.name = "ServerError";
  }
}

/** Raised when the connection to the server fails. */
export class ConnectionError extends SuperDevError {
  constructor(message = "Connection failed") {
    super(message, 0);
    this.name = "ConnectionError";
  }
}

/** Raised when a request times out. */
export class TimeoutError extends SuperDevError {
  constructor(message = "Request timed out") {
    super(message, 0);
    this.name = "TimeoutError";
  }
}

/**
 * Map an HTTP status code to the appropriate error class and throw it.
 * @internal
 */
export function throwHttpError(
  status: number,
  message: string,
  details: Record<string, unknown> = {},
): never {
  switch (status) {
    case 401:
      throw new AuthenticationError(message, details);
    case 403:
      throw new AuthorizationError(message, details);
    case 404:
      throw new NotFoundError(message, details);
    case 422:
      throw new ValidationError(message, details);
    case 429: {
      const retryAfter = details["retry_after"];
      throw new RateLimitError(
        message,
        typeof retryAfter === "number" ? retryAfter : null,
        details,
      );
    }
    case 500:
      throw new ServerError(message, details);
    default:
      throw new SuperDevError(message, status, details);
  }
}
