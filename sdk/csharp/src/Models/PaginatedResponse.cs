using System.Text.Json.Serialization;

namespace SuperDev.SDK.Models;

/// <summary>
/// A paginated response containing a list of items and pagination metadata.
/// </summary>
/// <typeparam name="T">The type of items in the response.</typeparam>
public sealed class PaginatedResponse<T>
{
    /// <summary>The items in the current page.</summary>
    [JsonPropertyName("items")]
    public List<T> Items { get; set; } = new();

    /// <summary>Total number of items across all pages.</summary>
    [JsonPropertyName("total")]
    public int Total { get; set; }

    /// <summary>Current page number (1-indexed).</summary>
    [JsonPropertyName("page")]
    public int Page { get; set; } = 1;

    /// <summary>Number of items per page.</summary>
    [JsonPropertyName("page_size")]
    public int PageSize { get; set; } = 20;

    /// <summary>Whether there is a next page.</summary>
    [JsonPropertyName("has_next")]
    public bool HasNext { get; set; }

    /// <summary>Whether there is a previous page.</summary>
    [JsonPropertyName("has_previous")]
    public bool HasPrevious { get; set; }
}
