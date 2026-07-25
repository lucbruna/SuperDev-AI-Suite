package com.superdev.sdk;

import com.google.gson.Gson;
import com.google.gson.reflect.TypeToken;
import com.superdev.sdk.auth.AuthManager;
import com.superdev.sdk.exceptions.AuthenticationException;
import com.superdev.sdk.exceptions.NotFoundException;
import com.superdev.sdk.exceptions.SuperDevException;
import com.superdev.sdk.types.*;

import java.lang.reflect.Type;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.List;
import java.util.concurrent.Flow;

/**
 * Main client for interacting with the SuperDev API.
 * Uses the builder pattern for construction.
 */
public class SuperDevClient {

    private final AuthManager authManager;
    private final HttpClient httpClient;
    private final Gson gson;
    private final Duration timeout;

    private SuperDevClient(Builder builder) {
        this.authManager = new AuthManager(builder.apiKey, builder.baseUrl);
        this.httpClient = HttpClient.newBuilder()
                .connectTimeout(builder.connectTimeout)
                .build();
        this.gson = new Gson();
        this.timeout = builder.requestTimeout;
    }

    /**
     * Creates a new builder for SuperDevClient.
     *
     * @return a new Builder instance
     */
    public static Builder builder() {
        return new Builder();
    }

    // ----------------- Users -----------------

    /**
     * Get a user by ID.
     *
     * @param userId the user ID
     * @return the User
     * @throws SuperDevException if the request fails
     */
    public User getUser(String userId) throws SuperDevException {
        return executeGet("/users/" + userId, User.class);
    }

    /**
     * List all users with pagination.
     *
     * @param page     the page number (1-indexed)
     * @param pageSize the number of items per page
     * @return a paginated response of users
     */
    public PaginatedResponse<User> listUsers(int page, int pageSize) {
        return executeGet("/users?page=" + page + "&pageSize=" + pageSize, 
                TypeToken.getParameterized(PaginatedResponse.class, User.class).getType());
    }

    // ----------------- Projects -----------------

    /**
     * Get a project by ID.
     *
     * @param projectId the project ID
     * @return the Project
     * @throws SuperDevException if the request fails
     */
    public Project getProject(String projectId) throws SuperDevException {
        return executeGet("/projects/" + projectId, Project.class);
    }

    /**
     * List all projects with pagination.
     *
     * @param page     the page number
     * @param pageSize the number of items per page
     * @return a paginated response of projects
     */
    public PaginatedResponse<Project> listProjects(int page, int pageSize) {
        return executeGet("/projects?page=" + page + "&pageSize=" + pageSize,
                TypeToken.getParameterized(PaginatedResponse.class, Project.class).getType());
    }

    // ----------------- Agents -----------------

    /**
     * Get an agent by ID.
     *
     * @param agentId the agent ID
     * @return the Agent
     * @throws SuperDevException if the request fails
     */
    public Agent getAgent(String agentId) throws SuperDevException {
        return executeGet("/agents/" + agentId, Agent.class);
    }

    /**
     * List all agents with pagination.
     *
     * @param page     the page number
     * @param pageSize the number of items per page
     * @return a paginated response of agents
     */
    public PaginatedResponse<Agent> listAgents(int page, int pageSize) {
        return executeGet("/agents?page=" + page + "&pageSize=" + pageSize,
                TypeToken.getParameterized(PaginatedResponse.class, Agent.class).getType());
    }

    // ----------------- Workflows -----------------

    /**
     * Get a workflow by ID.
     *
     * @param workflowId the workflow ID
     * @return the Workflow
     * @throws SuperDevException if the request fails
     */
    public Workflow getWorkflow(String workflowId) throws SuperDevException {
        return executeGet("/workflows/" + workflowId, Workflow.class);
    }

    /**
     * List all workflows with pagination.
     *
     * @param page     the page number
     * @param pageSize the number of items per page
     * @return a paginated response of workflows
     */
    public PaginatedResponse<Workflow> listWorkflows(int page, int pageSize) {
        return executeGet("/workflows?page=" + page + "&pageSize=" + pageSize,
                TypeToken.getParameterized(PaginatedResponse.class, Workflow.class).getType());
    }

    /**
     * Start a workflow execution.
     *
     * @param workflowId the ID of the workflow to run
     * @param input      the input data for the workflow (JSON string)
     * @return the WorkflowRun instance
     */
    public WorkflowRun runWorkflow(String workflowId, String input) {
        return executePost("/workflows/" + workflowId + "/run", input, WorkflowRun.class);
    }

    /**
     * Get the status and result of a workflow run.
     *
     * @param runId the run ID
     * @return the WorkflowRun details
     */
    public WorkflowRun getWorkflowRun(String runId) {
        return executeGet("/workflows/runs/" + runId, WorkflowRun.class);
    }

    // ----------------- Providers -----------------

    /**
     * List all providers.
     *
     * @return a list of providers
     */
    public List<Provider> listProviders() {
        return executeGet("/providers", new TypeToken<List<Provider>>() {}.getType());
    }

    // ----------------- Plugins -----------------

    /**
     * List all plugins.
     *
     * @return a list of plugins
     */
    public List<Plugin> listPlugins() {
        return executeGet("/plugins", new TypeToken<List<Plugin>>() {}.getType());
    }

    /**
     * Get a plugin by ID.
     *
     * @param pluginId the plugin ID
     * @return the Plugin details
     */
    public Plugin getPlugin(String pluginId) {
        return executeGet("/plugins/" + pluginId, Plugin.class);
    }

    // ----------------- Chat -----------------

    /**
     * Send a chat message to an agent and receive a response.
     *
     * @param agentId the ID of the agent to chat with
     * @param message the user message
     * @return the ChatResponse
     */
    public ChatResponse chat(String agentId, String message) {
        return executePost("/agents/" + agentId + "/chat", message, ChatResponse.class);
    }

    // ----------------- Deployments -----------------

    /**
     * Deploy a project to production.
     *
     * @param projectId the project ID to deploy
     * @return a status message or confirmation object (simplified as String for now)
     */
    public String deployProject(String projectId) {
        return executePost("/deployments/" + projectId, "", String.class);
    }

    // ----------------- Internal Helpers -----------------

    private <T> T executeGet(String path, Class<T> responseType) {
        try {
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(authManager.getBaseUrl() + path))
                    .header("Authorization", authManager.getAuthorizationHeader())
                    .header("Accept", "application/json")
                    .timeout(timeout)
                    .GET()
                    .build();

            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            return handleResponse(response, responseType);
        } catch (Exception e) {
            throw new SuperDevException("Request failed: " + e.getMessage(), e);
        }
    }

    private <T> T executeGet(String path, Type responseType) {
        try {
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(authManager.getBaseUrl() + path))
                    .header("Authorization", authManager.getAuthorizationHeader())
                    .header("Accept", "application/json")
                    .timeout(timeout)
                    .GET()
                    .build();

            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            return handleResponse(response, responseType);
        } catch (Exception e) {
            throw new SuperDevException("Request failed: " + e.getMessage(), e);
        }
    }

    private <T> T executePost(String path, String body, Class<T> responseType) {
        try {
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(authManager.getBaseUrl() + path))
                    .header("Authorization", authManager.getAuthorizationHeader())
                    .header("Content-Type", "application/json")
                    .timeout(timeout)
                    .POST(HttpRequest.BodyPublishers.ofString(body))
                    .build();

            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            return handleResponse(response, responseType);
        } catch (Exception e) {
            throw new SuperDevException("Request failed: " + e.getMessage(), e);
        }
    }

    private <T> T handleResponse(HttpResponse<String> response, Class<T> responseType) {
        int statusCode = response.statusCode();
        String body = response.body();

        if (statusCode == 200) {
            return gson.fromJson(body, responseType);
        } else if (statusCode == 401) {
            throw new AuthenticationException("Authentication failed: Invalid or missing API key");
        } else if (statusCode == 404) {
            throw new NotFoundException("Resource not found: " + body);
        } else {
            throw new SuperDevException("API request failed with status " + statusCode + ": " + body, statusCode);
        }
    }

    private <T> T handleResponse(HttpResponse<String> response, Type responseType) {
        int statusCode = response.statusCode();
        String body = response.body();

        if (statusCode == 200) {
            return gson.fromJson(body, responseType);
        } else if (statusCode == 401) {
            throw new AuthenticationException("Authentication failed: Invalid or missing API key");
        } else if (statusCode == 404) {
            throw new NotFoundException("Resource not found: " + body);
        } else {
            throw new SuperDevException("API request failed with status " + statusCode + ": " + body, statusCode);
        }
    }

    /**
     * Builder for constructing {@link SuperDevClient} instances.
     */
    public static class Builder {
        private String apiKey;
        private String baseUrl = "https://api.superdev.com/v1";
        private Duration connectTimeout = Duration.ofSeconds(10);
        private Duration requestTimeout = Duration.ofSeconds(30);

        /**
         * Sets the API key for authentication.
         *
         * @param apiKey the API key
         * @return this builder
         */
        public Builder apiKey(String apiKey) {
            this.apiKey = apiKey;
            return this;
        }

        /**
         * Sets the base URL for the API.
         *
         * @param baseUrl the base URL
         * @return this builder
         */
        public Builder baseUrl(String baseUrl) {
            this.baseUrl = baseUrl;
            return this;
        }

        /**
         * Sets the connection timeout.
         *
         * @param timeout the timeout duration
         * @return this builder
         */
        public Builder connectTimeout(Duration timeout) {
            this.connectTimeout = timeout;
            return this;
        }

        /**
         * Sets the request timeout.
         *
         * @param timeout the timeout duration
         * @return this builder
         */
        public Builder requestTimeout(Duration timeout) {
            this.requestTimeout = timeout;
            return this;
        }

        /**
         * Builds and returns the SuperDevClient instance.
         *
         * @return a new SuperDevClient
         * @throws IllegalArgumentException if the API key is not set
         */
        public SuperDevClient build() {
            if (apiKey == null || apiKey.isBlank()) {
                throw new IllegalArgumentException("API key must be provided");
            }
            return new SuperDevClient(this);
        }
    }
}
