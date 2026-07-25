using System.Text.Json;
using System.Text.Json.Serialization;

namespace SuperDev.SDK.Models;

/// <summary>
/// A chat message role.
/// </summary>
[JsonConverter(typeof(JsonStringEnumConverter))]
public enum MessageRole
{
    User,
    Assistant,
    System,
    Tool
}

/// <summary>
/// A single chat message.
/// </summary>
public sealed class ChatMessage
{
    /// <summary>Message role.</summary>
    [JsonPropertyName("role")]
    public MessageRole Role { get; set; }

    /// <summary>Message content.</summary>
    [JsonPropertyName("content")]
    public string Content { get; set; } = string.Empty;

    /// <summary>When the message was created.</summary>
    [JsonPropertyName("timestamp")]
    public DateTimeOffset? Timestamp { get; set; }

    /// <summary>Additional metadata.</summary>
    [JsonPropertyName("metadata")]
    public Dictionary<string, JsonElement> Metadata { get; set; } = new();
}

/// <summary>
/// Response from a chat completion request.
/// </summary>
public sealed class ChatResponse
{
    /// <summary>The generated message content.</summary>
    [JsonPropertyName("message")]
    public string Message { get; set; } = string.Empty;

    /// <summary>Model used for generation.</summary>
    [JsonPropertyName("model")]
    public string Model { get; set; } = string.Empty;

    /// <summary>Provider used for generation.</summary>
    [JsonPropertyName("provider")]
    public string Provider { get; set; } = string.Empty;

    /// <summary>Token usage statistics.</summary>
    [JsonPropertyName("usage")]
    public Dictionary<string, int> Usage { get; set; } = new();

    /// <summary>Reason the generation finished.</summary>
    [JsonPropertyName("finish_reason")]
    public string FinishReason { get; set; } = string.Empty;
}
