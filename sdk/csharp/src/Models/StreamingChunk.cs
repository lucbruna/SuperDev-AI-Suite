using System.Text.Json;
using System.Text.Json.Serialization;

namespace SuperDev.SDK.Models;

/// <summary>
/// A single chunk from a streaming chat response.
/// </summary>
public sealed class StreamingChunk
{
    /// <summary>Incremental text delta.</summary>
    [JsonPropertyName("delta")]
    public string Delta { get; set; } = string.Empty;

    /// <summary>Model used for generation.</summary>
    [JsonPropertyName("model")]
    public string Model { get; set; } = string.Empty;

    /// <summary>Reason the generation finished, or null if still streaming.</summary>
    [JsonPropertyName("finish_reason")]
    public string? FinishReason { get; set; }

    /// <summary>Token usage statistics.</summary>
    [JsonPropertyName("usage")]
    public Dictionary<string, int> Usage { get; set; } = new();
}
