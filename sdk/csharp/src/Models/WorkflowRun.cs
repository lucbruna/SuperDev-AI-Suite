using System.Text.Json;
using System.Text.Json.Serialization;

namespace SuperDev.SDK.Models;

/// <summary>
/// Possible workflow run statuses.
/// </summary>
[JsonConverter(typeof(JsonStringEnumConverter))]
public enum WorkflowRunStatus
{
    Pending,
    Running,
    Completed,
    Failed,
    Cancelled,
    Paused
}

/// <summary>
/// Represents a single execution of a workflow.
/// </summary>
public sealed class WorkflowRun
{
    /// <summary>Unique run identifier.</summary>
    [JsonPropertyName("id")]
    public string Id { get; set; } = string.Empty;

    /// <summary>The workflow this run belongs to.</summary>
    [JsonPropertyName("workflow_id")]
    public string WorkflowId { get; set; } = string.Empty;

    /// <summary>Current run status.</summary>
    [JsonPropertyName("status")]
    public WorkflowRunStatus Status { get; set; } = WorkflowRunStatus.Pending;

    /// <summary>Inputs provided to the workflow run.</summary>
    [JsonPropertyName("inputs")]
    public Dictionary<string, JsonElement> Inputs { get; set; } = new();

    /// <summary>Outputs produced by the workflow run.</summary>
    [JsonPropertyName("outputs")]
    public Dictionary<string, JsonElement> Outputs { get; set; } = new();

    /// <summary>When the run started.</summary>
    [JsonPropertyName("started_at")]
    public DateTimeOffset? StartedAt { get; set; }

    /// <summary>When the run finished.</summary>
    [JsonPropertyName("finished_at")]
    public DateTimeOffset? FinishedAt { get; set; }

    /// <summary>Error message if the run failed.</summary>
    [JsonPropertyName("error")]
    public string? Error { get; set; }
}
