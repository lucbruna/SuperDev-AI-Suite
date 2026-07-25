using System.Text.Json.Serialization;

namespace SuperDev.SDK.Models;

/// <summary>
/// Represents a SuperDev user.
/// </summary>
public sealed class User
{
    /// <summary>Unique user identifier.</summary>
    [JsonPropertyName("id")]
    public string Id { get; set; } = string.Empty;

    /// <summary>User email address.</summary>
    [JsonPropertyName("email")]
    public string Email { get; set; } = string.Empty;

    /// <summary>Display name.</summary>
    [JsonPropertyName("name")]
    public string Name { get; set; } = string.Empty;

    /// <summary>URL to the user's avatar image.</summary>
    [JsonPropertyName("avatar_url")]
    public string? AvatarUrl { get; set; }

    /// <summary>Whether the user account is active.</summary>
    [JsonPropertyName("is_active")]
    public bool IsActive { get; set; } = true;

    /// <summary>When the user was created.</summary>
    [JsonPropertyName("created_at")]
    public DateTimeOffset? CreatedAt { get; set; }

    /// <summary>When the user was last updated.</summary>
    [JsonPropertyName("updated_at")]
    public DateTimeOffset? UpdatedAt { get; set; }
}
