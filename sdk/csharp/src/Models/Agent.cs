using System.Text.Json;
using System.Text.Json.Serialization;

namespace SuperDev.SDK.Models;

/// <summary>
/// Possible agent statuses.
/// </summary>
[JsonConverter(typeof(JsonStringEnumConverter))]
public enum AgentStatus
{
    Idle,
    Running,
    Paused,
    Error,
    Stopped
}

/// <summary>
/// Represents a SuperDev AI agent.
/// </summary>
public sealed class Agent
{
    /// <summary>Unique agent identifier.</summary>
    [JsonPropertyName("id")]
    public string Id { get; set; } = string.Empty;

    /// <summary>Agent name.</summary>
    [JsonPropertyName("name")]
    public string Name { get; set; } = string.Empty;

    /// <summary>Agent type (e.g. "general", "coding", "research").</summary>
    [JsonPropertyName("type")]
    public string Type { get; set; } = "general";

    /// <summary>Current agent status.</summary>
    [JsonPropertyName("status")]
    public AgentStatus Status { get; set; } = AgentStatus.Idle;

    /// <summary>Agent configuration parameters.</summary>
    [JsonPropertyName("config")]
    public Dictionary<string, JsonElement> Config { get; set; } = new();

    /// <summary>When the agent was created.</summary>
    [JsonPropertyName("created_at")]
    public DateTimeOffset? CreatedAt { get; set; }
}
