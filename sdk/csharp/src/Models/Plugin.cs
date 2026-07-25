using System.Text.Json;
using System.Text.Json.Serialization;

namespace SuperDev.SDK.Models;

/// <summary>
/// Represents a SuperDev plugin.
/// </summary>
public sealed class Plugin
{
    /// <summary>Unique plugin identifier.</summary>
    [JsonPropertyName("id")]
    public string Id { get; set; } = string.Empty;

    /// <summary>Plugin name.</summary>
    [JsonPropertyName("name")]
    public string Name { get; set; } = string.Empty;

    /// <summary>Plugin version.</summary>
    [JsonPropertyName("version")]
    public string Version { get; set; } = "0.1.0";

    /// <summary>Plugin description.</summary>
    [JsonPropertyName("description")]
    public string Description { get; set; } = string.Empty;

    /// <summary>Plugin author.</summary>
    [JsonPropertyName("author")]
    public string Author { get; set; } = string.Empty;

    /// <summary>Whether the plugin is currently installed.</summary>
    [JsonPropertyName("is_installed")]
    public bool IsInstalled { get; set; }

    /// <summary>Plugin configuration.</summary>
    [JsonPropertyName("config")]
    public Dictionary<string, JsonElement> Config { get; set; } = new();
}
