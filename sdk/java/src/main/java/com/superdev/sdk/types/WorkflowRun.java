package com.superdev.sdk.types;

import java.util.Objects;

/**
 * Represents a specific execution run of a workflow.
 */
public final class WorkflowRun {
    private final String id;
    private final String workflowId;
    private final String status;
    private final String input;
    private final String output;
    private final long startedAt;
    private final long finishedAt;

    public WorkflowRun(String id, String workflowId, String status, String input, String output, long startedAt, long finishedAt) {
        this.id = id;
        this.workflowId = workflowId;
        this.status = status;
        this.input = input;
        this.output = output;
        this.startedAt = startedAt;
        this.finishedAt = finishedAt;
    }

    public String getId() { return id; }
    public String getWorkflowId() { return workflowId; }
    public String getStatus() { return status; }
    public String getInput() { return input; }
    public String getOutput() { return output; }
    public long getStartedAt() { return startedAt; }
    public long getFinishedAt() { return finishedAt; }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        WorkflowRun that = (WorkflowRun) o;
        return Objects.equals(id, that.id);
    }

    @Override
    public int hashCode() {
        return Objects.hash(id);
    }

    @Override
    public String toString() {
        return "WorkflowRun{id='" + id + "', status='" + status + "'}";
    }
}
