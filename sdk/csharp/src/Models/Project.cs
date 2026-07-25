using System.Text.Json.Serialization;

namespace SuperDev.SDK.Models;

/// <summary>
/// Represents a SuperDev project.
/// </summary>
public sealed class Project
{
    /// <summary>Unique project identifier.</summary>
    [JsonPropertyName("id")]
    public string Id { get; set; } = string.Empty;

    /// <summary>Project name.</summary>
    [JsonPropertyName("name")]
    public string Name { get; set; } = string.Empty;

    /// <summary>Project description.</summary>
    [JsonPropertyName("description")]
    public string Description { get; set; } = string.Empty;

    /// <summary>Owner organization identifier.</summary>
    [JsonPropertyName("organization_id")]
    public string OrganizationId { get; set; } = string.Empty;

    /// <summary>Current project status.</summary>
    [JsonPropertyName("status")]
    public string Status { get; set; } = "active";

    /// <summary>When the project was created.</summary>
    [JsonPropertyName("created_at")]
    public DateTimeOffset? CreatedAt { get; set; }

    /// <summary>When the project was last updated.</summary>
    [JsonPropertyName("updated_at")]
    public DateTimeOffset? UpdatedAt { get; set; }
}
