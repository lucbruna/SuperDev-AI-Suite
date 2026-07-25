package com.superdev.sdk.exceptions;

/**
 * Thrown when authentication fails (e.g., invalid or missing API key).
 */
public class AuthenticationException extends SuperDevException {

    /**
     * Creates a new AuthenticationException.
     *
     * @param message the error message
     */
    public AuthenticationException(String message) {
        super(message, 401);
    }

    /**
     * Creates a new AuthenticationException with a cause.
     *
     * @param message the error message
     * @param cause   the underlying cause
     */
    public AuthenticationException(String message, Throwable cause) {
        super(message, cause);
    }
}
