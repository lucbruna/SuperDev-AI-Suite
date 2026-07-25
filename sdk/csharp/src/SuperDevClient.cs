using System.Net;
using System.Net.Http.Headers;
using System.Net.Http.Json;
using System.Runtime.CompilerServices;
using System.Text;
using System.Text.Json;
using Microsoft.Extensions.DependencyInjection;
using SuperDev.SDK.Auth;
using SuperDev.SDK.Exceptions;
using SuperDev.SDK.Models;

namespace SuperDev.SDK;

/// <summary>
/// Configuration options for <see cref="SuperDevClient"/>.
/// </summary>
public sealed class SuperDevClientOptions
{
    /// <summary>Base URL of the SuperDev API.</summary>
    public string BaseUrl { get; set; } = "http://localhost:8000";

    /// <summary>API key for authentication.</summary>
    public string? ApiKey { get; set; }

    /// <summary>Default request timeout.</summary>
    public TimeSpan Timeout { get; set; } = TimeSpan.FromSeconds(30);
}

/// <summary>
/// Main client for the SuperDev AI Suite API.
/// </summary>
public sealed class SuperDevClient : IDisposable
{
    private readonly HttpClient _http;
    private readonly AuthManager _auth;
    private readonly bool _ownsHttpClient;
    private readonly JsonSerializerOptions _json = new()
    {
        PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower,
        PropertyNameCaseInsensitive = true
    };

    /// <summary>Users API.</summary>
    public UserApi Users => new(this);
    /// <summary>Projects API.</summary>
    public ProjectApi Projects => new(this);
    /// <summary>Agents API.</summary>
    public AgentApi Agents => new(this);
    /// <summary>Workflows API.</summary>
    public WorkflowApi Workflows => new(this);
    /// <summary>Providers API.</summary>
    public ProviderApi Providers => new(this);
    /// <summary>Plugins API.</summary>
    public PluginApi Plugins => new(this);
    /// <summary>Chat API.</summary>
    public ChatApi Chat => new(this);

    /// <summary>
    /// Creates a new <see cref="SuperDevClient"/> with the specified options.
    /// </summary>
    public SuperDevClient(SuperDevClientOptions options)
    {
        _http = new HttpClient { BaseAddress = new Uri(options.BaseUrl), Timeout = options.Timeout };
        _auth = new AuthManager(options.ApiKey);
        _ownsHttpClient = true;
    }

    /// <summary>
    /// Creates a new <see cref="SuperDevClient"/> using an existing <see cref="HttpClient"/>.
    /// </summary>
    public SuperDevClient(HttpClient httpClient, AuthManager auth)
    {
        _http = httpClient ?? throw new ArgumentNullException(nameof(httpClient));
        _auth = auth ?? throw new ArgumentNullException(nameof(auth));
        _ownsHttpClient = false;
    }

    /// <summary>
    /// Creates a pre-configured <see cref="SuperDevClient"/>.
    /// </summary>
    public static SuperDevClient Create(string baseUrl = "http://localhost:8000", string? apiKey = null)
        => new(new SuperDevClientOptions { BaseUrl = baseUrl, ApiKey = apiKey });

    /// <summary>
    /// Authenticates with email and password.
    /// </summary>
    public async Task<User> LoginAsync(string email, string password, CancellationToken ct = default)
    {
        var resp = await PostAsync<JsonElement>("/api/v1/auth/login",
            new { email, password }, auth: false, ct: ct);

        _auth.SetTokens(
            resp.GetProperty("access_token").GetString()!,
            resp.GetProperty("refresh_token").GetString()!,
            resp.TryGetProperty("expires_in", out var ei) ? ei.GetInt32() : 3600);

        return JsonSerializer.Deserialize<User>(resp.GetProperty("user").GetRawText(), _json)!;
    }

    /// <summary>
    /// Clears stored authentication tokens.
    /// </summary>
    public void Logout() => _auth.ClearTokens();

    // ── Low-level HTTP helpers ─────────────────────────────────────

    internal async Task<T> GetAsync<T>(string path, CancellationToken ct = default)
    {
        using var req = new HttpRequestMessage(HttpMethod.Get, path);
        var resp = await SendAsync(req, ct: ct);
        return await DeserializeResponseAsync<T>(resp, ct);
    }

    internal async Task<T> PostAsync<T>(string path, object? body = null, bool auth = true, CancellationToken ct = default)
    {
        using var req = new HttpRequestMessage(HttpMethod.Post, path);
        if (body is not null)
            req.Content = JsonContent.Create(body, options: _json);
        var resp = await SendAsync(req, auth: auth, ct: ct);
        return await DeserializeResponseAsync<T>(resp, ct);
    }

    internal async Task<T> PutAsync<T>(string path, object body, CancellationToken ct = default)
    {
        using var req = new HttpRequestMessage(HttpMethod.Put, path);
        req.Content = JsonContent.Create(body, options: _json);
        var resp = await SendAsync(req, ct: ct);
        return await DeserializeResponseAsync<T>(resp, ct);
    }

    internal async Task<T> PatchAsync<T>(string path, object body, CancellationToken ct = default)
    {
        using var req = new HttpRequestMessage(HttpMethod.Patch, path);
        req.Content = JsonContent.Create(body, options: _json);
        var resp = await SendAsync(req, ct: ct);
        return await DeserializeResponseAsync<T>(resp, ct);
    }

    internal async Task DeleteAsync(string path, CancellationToken ct = default)
    {
        using var req = new HttpRequestMessage(HttpMethod.Delete, path);
        await SendAsync(req, ct: ct);
    }

    internal async IAsyncEnumerable<StreamingChunk> StreamPostAsync(
        string path, object body, [EnumeratorCancellation] CancellationToken ct = default)
    {
        using var req = new HttpRequestMessage(HttpMethod.Post, path);
        req.Content = JsonContent.Create(body, options: _json);
        req.Headers.Add("Accept", "text/event-stream");

        var resp = await SendAsync(req, stream: true, ct: ct);
        resp.EnsureSuccessStatusCode();

        using var stream = await resp.Content.ReadAsStreamAsync(ct);
        using var reader = new StreamReader(stream, Encoding.UTF8);

        while (!reader.EndOfStream)
        {
            ct.ThrowIfCancellationRequested();
            var line = await reader.ReadLineAsync(ct);
            if (string.IsNullOrEmpty(line) || !line.StartsWith("data: "))
                continue;

            var payload = line[6..];
            if (payload == "[DONE]")
                break;

            StreamingChunk? chunk = null;
            try
            {
                chunk = JsonSerializer.Deserialize<StreamingChunk>(payload, _json);
            }
            catch (JsonException)
            {
                // skip malformed chunks
            }

            if (chunk is not null)
                yield return chunk;
        }
    }

    private async Task<HttpResponseMessage> SendAsync(
        HttpRequestMessage req, bool auth = true, bool stream = false, CancellationToken ct = default)
    {
        req.Headers.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));
        if (auth)
            req.Headers.Authorization = AuthenticationHeaderValue.Parse(_auth.GetAuthorizationHeader());

        HttpResponseMessage resp;
        try
        {
            resp = stream
                ? await _http.SendAsync(req, HttpCompletionOption.ResponseHeadersRead, ct)
                : await _http.SendAsync(req, ct);
        }
        catch (HttpRequestException ex) when (ex.StatusCode is null)
        {
            throw new SuperDevException($"Connection failed: {ex.Message}", ex);
        }
        catch (TaskCanceledException ex) when (ex.InnerException is TimeoutException)
        {
            throw new SuperDevException("Request timed out", ex);
        }

        await HandleErrorResponseAsync(resp, ct);
        return resp;
    }

    private async Task HandleErrorResponseAsync(HttpResponseMessage resp, CancellationToken ct)
    {
        if (resp.IsSuccessStatusCode) return;

        var body = await resp.Content.ReadAsStringAsync(ct);
        Dictionary<string, object>? details = null;
        try
        {
            details = JsonSerializer.Deserialize<Dictionary<string, object>>(body, _json);
        }
        catch { /* non-JSON error body */ }

        var message = details?.TryGetValue("message", out var msg) == true ? msg!.ToString()
                    : details?.TryGetValue("error", out var err) == true ? err!.ToString()
                    : $"HTTP {(int)resp.StatusCode}: {resp.ReasonPhrase}";

        throw resp.StatusCode switch
        {
            HttpStatusCode.Unauthorized or HttpStatusCode.Forbidden
                => new AuthenticationException(message!, details),
            HttpStatusCode.NotFound
                => new NotFoundException(message!, details),
            _ => new SuperDevException(message!, resp.StatusCode, details)
        };
    }

    private async Task<T> DeserializeResponseAsync<T>(HttpResponseMessage resp, CancellationToken ct)
    {
        var body = await resp.Content.ReadAsStringAsync(ct);
        if (string.IsNullOrWhiteSpace(body) && typeof(T) == typeof(object))
            return default!;
        return JsonSerializer.Deserialize<T>(body, _json)!;
    }

    public void Dispose()
    {
        if (_ownsHttpClient)
            _http.Dispose();
    }
}

/// <summary>
/// DI extension methods for registering <see cref="SuperDevClient"/>.
/// </summary>
public static class SuperDevServiceCollectionExtensions
{
    /// <summary>
    /// Registers <see cref="SuperDevClient"/> and <see cref="AuthManager"/> in the DI container.
    /// </summary>
    public static IServiceCollection AddSuperDevSDK(
        this IServiceCollection services,
        Action<SuperDevClientOptions>? configure = null)
    {
        var options = new SuperDevClientOptions();
        configure?.Invoke(options);

        services.AddSingleton(new AuthManager(options.ApiKey));
        services.AddHttpClient<SuperDevClient>(client =>
        {
            client.BaseAddress = new Uri(options.BaseUrl);
            client.Timeout = options.Timeout;
        });

        return services;
    }
}

// ── Resource API classes ──────────────────────────────────────────

/// <summary>API methods for managing users.</summary>
public sealed class UserApi
{
    private readonly SuperDevClient _c;
    internal UserApi(SuperDevClient client) => _c = client;

    /// <summary>Gets the currently authenticated user.</summary>
    public Task<User> MeAsync(CancellationToken ct = default)
        => _c.GetAsync<User>("/api/v1/users/me", ct);

    /// <summary>Lists users with pagination.</summary>
    public Task<PaginatedResponse<User>> ListAsync(int page = 1, int pageSize = 20, CancellationToken ct = default)
        => _c.GetAsync<PaginatedResponse<User>>($"/api/v1/users?page={page}&page_size={pageSize}", ct);
}

/// <summary>API methods for managing projects.</summary>
public sealed class ProjectApi
{
    private readonly SuperDevClient _c;
    internal ProjectApi(SuperDevClient client) => _c = client;

    /// <summary>Lists projects with pagination.</summary>
    public Task<PaginatedResponse<Project>> ListAsync(int page = 1, int pageSize = 20, CancellationToken ct = default)
        => _c.GetAsync<PaginatedResponse<Project>>($"/api/v1/projects?page={page}&page_size={pageSize}", ct);

    /// <summary>Gets a project by ID.</summary>
    public Task<Project> GetAsync(string projectId, CancellationToken ct = default)
        => _c.GetAsync<Project>($"/api/v1/projects/{projectId}", ct);

    /// <summary>Creates a new project.</summary>
    public Task<Project> CreateAsync(string name, string description = "", CancellationToken ct = default)
        => _c.PostAsync<Project>("/api/v1/projects", new { name, description }, ct: ct);

    /// <summary>Updates a project.</summary>
    public Task<Project> UpdateAsync(string projectId, Dictionary<string, object> updates, CancellationToken ct = default)
        => _c.PatchAsync<Project>($"/api/v1/projects/{projectId}", updates, ct);

    /// <summary>Deletes a project.</summary>
    public Task DeleteAsync(string projectId, CancellationToken ct = default)
        => _c.DeleteAsync($"/api/v1/projects/{projectId}", ct);
}

/// <summary>API methods for managing agents.</summary>
public sealed class AgentApi
{
    private readonly SuperDevClient _c;
    internal AgentApi(SuperDevClient client) => _c = client;

    /// <summary>Lists agents with pagination.</summary>
    public Task<PaginatedResponse<Agent>> ListAsync(int page = 1, int pageSize = 20, CancellationToken ct = default)
        => _c.GetAsync<PaginatedResponse<Agent>>($"/api/v1/agents?page={page}&page_size={pageSize}", ct);

    /// <summary>Gets an agent by ID.</summary>
    public Task<Agent> GetAsync(string agentId, CancellationToken ct = default)
        => _c.GetAsync<Agent>($"/api/v1/agents/{agentId}", ct);

    /// <summary>Starts an agent with optional configuration.</summary>
    public Task<Agent> StartAsync(string agentId, Dictionary<string, object>? config = null, CancellationToken ct = default)
        => _c.PostAsync<Agent>($"/api/v1/agents/{agentId}/start", config ?? new(), ct: ct);

    /// <summary>Stops a running agent.</summary>
    public Task<Agent> StopAsync(string agentId, CancellationToken ct = default)
        => _c.PostAsync<Agent>($"/api/v1/agents/{agentId}/stop", ct: ct);

    /// <summary>Gets agent logs.</summary>
    public Task<List<JsonElement>> LogsAsync(string agentId, int limit = 100, CancellationToken ct = default)
        => _c.GetAsync<List<JsonElement>>($"/api/v1/agents/{agentId}/logs?limit={limit}", ct);
}

/// <summary>API methods for managing workflows.</summary>
public sealed class WorkflowApi
{
    private readonly SuperDevClient _c;
    internal WorkflowApi(SuperDevClient client) => _c = client;

    /// <summary>Lists workflows with pagination.</summary>
    public Task<PaginatedResponse<Workflow>> ListAsync(int page = 1, int pageSize = 20, CancellationToken ct = default)
        => _c.GetAsync<PaginatedResponse<Workflow>>($"/api/v1/workflows?page={page}&page_size={pageSize}", ct);

    /// <summary>Gets a workflow by ID.</summary>
    public Task<Workflow> GetAsync(string workflowId, CancellationToken ct = default)
        => _c.GetAsync<Workflow>($"/api/v1/workflows/{workflowId}", ct);

    /// <summary>Creates a new workflow.</summary>
    public Task<Workflow> CreateAsync(string name, Dictionary<string, object> graph, string description = "", CancellationToken ct = default)
        => _c.PostAsync<Workflow>("/api/v1/workflows", new { name, graph, description }, ct: ct);

    /// <summary>Runs a workflow with the given inputs.</summary>
    public Task<WorkflowRun> RunAsync(string workflowId, Dictionary<string, object>? inputs = null, CancellationToken ct = default)
        => _c.PostAsync<WorkflowRun>($"/api/v1/workflows/{workflowId}/run", new { inputs = inputs ?? new() }, ct: ct);

    /// <summary>Gets the status of a workflow run.</summary>
    public Task<WorkflowRun> GetRunAsync(string workflowId, string runId, CancellationToken ct = default)
        => _c.GetAsync<WorkflowRun>($"/api/v1/workflows/{workflowId}/runs/{runId}", ct);

    /// <summary>Cancels a running workflow.</summary>
    public Task<WorkflowRun> CancelRunAsync(string workflowId, string runId, CancellationToken ct = default)
        => _c.PostAsync<WorkflowRun>($"/api/v1/workflows/{workflowId}/runs/{runId}/cancel", ct: ct);

    /// <summary>Deletes a workflow.</summary>
    public Task DeleteAsync(string workflowId, CancellationToken ct = default)
        => _c.DeleteAsync($"/api/v1/workflows/{workflowId}", ct);
}

/// <summary>API methods for managing providers.</summary>
public sealed class ProviderApi
{
    private readonly SuperDevClient _c;
    internal ProviderApi(SuperDevClient client) => _c = client;

    /// <summary>Lists all providers.</summary>
    public Task<List<Provider>> ListAsync(CancellationToken ct = default)
        => _c.GetAsync<List<Provider>>("/api/v1/providers", ct);

    /// <summary>Gets health status of a provider.</summary>
    public Task<ProviderHealth> HealthAsync(string providerId, CancellationToken ct = default)
        => _c.GetAsync<ProviderHealth>($"/api/v1/providers/{providerId}/health", ct);

    /// <summary>Enables a provider.</summary>
    public Task<Provider> EnableAsync(string providerId, CancellationToken ct = default)
        => _c.PostAsync<Provider>($"/api/v1/providers/{providerId}/enable", ct: ct);

    /// <summary>Disables a provider.</summary>
    public Task<Provider> DisableAsync(string providerId, CancellationToken ct = default)
        => _c.PostAsync<Provider>($"/api/v1/providers/{providerId}/disable", ct: ct);

    /// <summary>Updates provider configuration.</summary>
    public Task<Provider> ConfigureAsync(string providerId, Dictionary<string, object> config, CancellationToken ct = default)
        => _c.PutAsync<Provider>($"/api/v1/providers/{providerId}/config", config, ct);
}

/// <summary>API methods for managing plugins.</summary>
public sealed class PluginApi
{
    private readonly SuperDevClient _c;
    internal PluginApi(SuperDevClient client) => _c = client;

    /// <summary>Lists all plugins.</summary>
    public Task<List<Plugin>> ListAsync(CancellationToken ct = default)
        => _c.GetAsync<List<Plugin>>("/api/v1/plugins", ct);

    /// <summary>Installs a plugin.</summary>
    public Task<Plugin> InstallAsync(string pluginId, CancellationToken ct = default)
        => _c.PostAsync<Plugin>($"/api/v1/plugins/{pluginId}/install", ct: ct);

    /// <summary>Uninstalls a plugin.</summary>
    public Task UninstallAsync(string pluginId, CancellationToken ct = default)
        => _c.DeleteAsync($"/api/v1/plugins/{pluginId}", ct);

    /// <summary>Updates a plugin.</summary>
    public Task<Plugin> UpdateAsync(string pluginId, CancellationToken ct = default)
        => _c.PostAsync<Plugin>($"/api/v1/plugins/{pluginId}/update", ct: ct);
}

/// <summary>API methods for chat interactions.</summary>
public sealed class ChatApi
{
    private readonly SuperDevClient _c;
    internal ChatApi(SuperDevClient client) => _c = client;

    /// <summary>Sends a chat message and returns a completion response.</summary>
    public Task<ChatResponse> SendAsync(
        string message,
        string? model = null,
        string? provider = null,
        string? conversationId = null,
        string? systemPrompt = null,
        CancellationToken ct = default)
    {
        var payload = new Dictionary<string, object> { ["message"] = message };
        if (model is not null) payload["model"] = model;
        if (provider is not null) payload["provider"] = provider;
        if (conversationId is not null) payload["conversation_id"] = conversationId;
        if (systemPrompt is not null) payload["system_prompt"] = systemPrompt;
        return _c.PostAsync<ChatResponse>("/api/v1/chat", payload, ct: ct);
    }

    /// <summary>Sends a chat message and returns a streaming response.</summary>
    public IAsyncEnumerable<StreamingChunk> StreamAsync(
        string message,
        string? model = null,
        string? provider = null,
        string? conversationId = null,
        CancellationToken ct = default)
    {
        var payload = new Dictionary<string, object> { ["message"] = message, ["stream"] = true };
        if (model is not null) payload["model"] = model;
        if (provider is not null) payload["provider"] = provider;
        if (conversationId is not null) payload["conversation_id"] = conversationId;
        return _c.StreamPostAsync("/api/v1/chat", payload, ct);
    }

    /// <summary>Lists recent conversations.</summary>
    public Task<List<JsonElement>> ConversationsAsync(CancellationToken ct = default)
        => _c.GetAsync<List<JsonElement>>("/api/v1/chat/conversations", ct);

    /// <summary>Generates embeddings for the given input text.</summary>
    public Task<JsonElement> EmbeddingsAsync(
        string input,
        string model = "text-embedding-3-small",
        CancellationToken ct = default)
        => _c.PostAsync<JsonElement>("/api/v1/chat/embeddings", new { input, model }, ct: ct);
}
