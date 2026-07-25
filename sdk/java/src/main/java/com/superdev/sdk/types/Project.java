package com.superdev.sdk.types;

import java.util.Objects;

/**
 * Represents a project in the SuperDev system.
 */
public final class Project {
    private final String id;
    private final String name;
    private final String description;
    private final String ownerId;
    private final String status;
    private final long createdAt;

    public Project(String id, String name, String description, String ownerId, String status, long createdAt) {
        this.id = id;
        this.name = name;
        this.description = description;
        this.ownerId = ownerId;
        this.status = status;
        this.createdAt = createdAt;
    }

    public String getId() { return id; }
    public String getName() { return name; }
    public String getDescription() { return description; }
    public String getOwnerId() { return ownerId; }
    public String getStatus() { return status; }
    public long getCreatedAt() { return createdAt; }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Project project = (Project) o;
        return Objects.equals(id, project.id);
    }

    @Override
    public int hashCode() {
        return Objects.hash(id);
    }

    @Override
    public String toString() {
        return "Project{id='" + id + "', name='" + name + "', status='" + status + "'}";
    }
}
