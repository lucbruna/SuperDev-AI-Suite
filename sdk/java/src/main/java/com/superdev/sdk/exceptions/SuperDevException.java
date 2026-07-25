package com.superdev.sdk.exceptions;

/**
 * Base exception class for all SuperDev SDK errors.
 */
public class SuperDevException extends RuntimeException {

    private final int statusCode;

    /**
     * Creates a new SuperDevException.
     *
     * @param message the error message
     */
    public SuperDevException(String message) {
        super(message);
        this.statusCode = -1;
    }

    /**
     * Creates a new SuperDevException with a cause.
     *
     * @param message the error message
     * @param cause   the underlying cause
     */
    public SuperDevException(String message, Throwable cause) {
        super(message, cause);
        this.statusCode = -1;
    }

    /**
     * Creates a new SuperDevException with a status code.
     *
     * @param message    the error message
     * @param statusCode the HTTP status code
     */
    public SuperDevException(String message, int statusCode) {
        super(message);
        this.statusCode = statusCode;
    }

    /**
     * Returns the HTTP status code associated with this error.
     *
     * @return the status code, or -1 if not applicable
     */
    public int getStatusCode() {
        return statusCode;
    }
}
