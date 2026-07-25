package com.superdev.sdk.types;

import java.util.Objects;

/**
 * Represents a workflow in the SuperDev system.
 */
public final class Workflow {
    private final String id;
    private final String name;
    private final String description;
    private final String status;
    private final long createdAt;

    public Workflow(String id, String name, String description, String status, long createdAt) {
        this.id = id;
        this.name = name;
        this.description = description;
        this.status = status;
        this.createdAt = createdAt;
    }

    public String getId() { return id; }
    public String getName() { return name; }
    public String getDescription() { return description; }
    public String getStatus() { return status; }
    public long getCreatedAt() { return createdAt; }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Workflow workflow = (Workflow) o;
        return Objects.equals(id, workflow.id);
    }

    @Override
    public int hashCode() {
        return Objects.hash(id);
    }

    @Override
    public String toString() {
        return "Workflow{id='" + id + "', name='" + name + "', status='" + status + "'}";
    }
}
