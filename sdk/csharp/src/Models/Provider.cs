using System.Text.Json;
using System.Text.Json.Serialization;

namespace SuperDev.SDK.Models;

/// <summary>
/// Represents an AI model provider (e.g. OpenAI, Anthropic).
/// </summary>
public sealed class Provider
{
    /// <summary>Unique provider identifier.</summary>
    [JsonPropertyName("id")]
    public string Id { get; set; } = string.Empty;

    /// <summary>Provider display name.</summary>
    [JsonPropertyName("name")]
    public string Name { get; set; } = string.Empty;

    /// <summary>Provider type identifier.</summary>
    [JsonPropertyName("type")]
    public string Type { get; set; } = string.Empty;

    /// <summary>Whether the provider is currently enabled.</summary>
    [JsonPropertyName("is_enabled")]
    public bool IsEnabled { get; set; } = true;

    /// <summary>Provider-specific configuration.</summary>
    [JsonPropertyName("config")]
    public Dictionary<string, JsonElement> Config { get; set; } = new();

    /// <summary>Current health status of the provider.</summary>
    [JsonPropertyName("health")]
    public string Health { get; set; } = "healthy";
}

/// <summary>
/// Health check result for a provider.
/// </summary>
public sealed class ProviderHealth
{
    /// <summary>Provider identifier.</summary>
    [JsonPropertyName("provider_id")]
    public string ProviderId { get; set; } = string.Empty;

    /// <summary>Current health status.</summary>
    [JsonPropertyName("status")]
    public string Status { get; set; } = string.Empty;

    /// <summary>Response latency in milliseconds.</summary>
    [JsonPropertyName("latency_ms")]
    public double LatencyMs { get; set; }

    /// <summary>When the health check was performed.</summary>
    [JsonPropertyName("last_checked")]
    public DateTimeOffset? LastChecked { get; set; }

    /// <summary>Error message if the provider is unhealthy.</summary>
    [JsonPropertyName("error")]
    public string? Error { get; set; }
}
