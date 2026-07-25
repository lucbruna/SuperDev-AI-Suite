package com.superdev.sdk.exceptions;

/**
 * Thrown when a requested resource is not found (e.g., 404 error).
 */
public class NotFoundException extends SuperDevException {

    /**
     * Creates a new NotFoundException.
     *
     * @param message the error message
     */
    public NotFoundException(String message) {
        super(message, 404);
    }

    /**
     * Creates a new NotFoundException with a cause.
     *
     * @param message the error message
     * @param cause   the underlying cause
     */
    public NotFoundException(String message, Throwable cause) {
        super(message, cause);
    }
}
