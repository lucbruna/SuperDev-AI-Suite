package com.superdev.sdk.auth;

/**
 * Manages authentication for the SuperDev API.
 * Handles API key storage and request header injection.
 */
public final class AuthManager {
    private final String apiKey;
    private final String baseUrl;

    /**
     * Creates a new AuthManager.
     *
     * @param apiKey  the API key for authentication
     * @param baseUrl the base URL of the SuperDev API
     */
    public AuthManager(String apiKey, String baseUrl) {
        if (apiKey == null || apiKey.isBlank()) {
            throw new IllegalArgumentException("API key cannot be null or blank");
        }
        this.apiKey = apiKey;
        this.baseUrl = baseUrl;
    }

    /**
     * Returns the API key.
     *
     * @return the API key
     */
    public String getApiKey() {
        return apiKey;
    }

    /**
     * Returns the base URL.
     *
     * @return the base URL
     */
    public String getBaseUrl() {
        return baseUrl;
    }

    /**
     * Returns the authorization header value.
     *
     * @return the Bearer token string
     */
    public String getAuthorizationHeader() {
        return "Bearer " + apiKey;
    }
}
