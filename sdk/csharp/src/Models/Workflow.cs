using System.Text.Json;
using System.Text.Json.Serialization;

namespace SuperDev.SDK.Models;

/// <summary>
/// Represents a SuperDev workflow definition.
/// </summary>
public sealed class Workflow
{
    /// <summary>Unique workflow identifier.</summary>
    [JsonPropertyName("id")]
    public string Id { get; set; } = string.Empty;

    /// <summary>Workflow name.</summary>
    [JsonPropertyName("name")]
    public string Name { get; set; } = string.Empty;

    /// <summary>Workflow description.</summary>
    [JsonPropertyName("description")]
    public string Description { get; set; } = string.Empty;

    /// <summary>The workflow graph definition (nodes and edges).</summary>
    [JsonPropertyName("graph")]
    public Dictionary<string, JsonElement> Graph { get; set; } = new();

    /// <summary>Current workflow status.</summary>
    [JsonPropertyName("status")]
    public string Status { get; set; } = "draft";

    /// <summary>Workflow version number.</summary>
    [JsonPropertyName("version")]
    public int Version { get; set; } = 1;

    /// <summary>When the workflow was created.</summary>
    [JsonPropertyName("created_at")]
    public DateTimeOffset? CreatedAt { get; set; }
}
