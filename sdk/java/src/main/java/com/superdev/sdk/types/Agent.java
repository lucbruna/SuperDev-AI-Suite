package com.superdev.sdk.types;

import java.util.Objects;

/**
 * Represents an AI agent in the SuperDev system.
 */
public final class Agent {
    private final String id;
    private final String name;
    private final String model;
    private final String systemPrompt;
    private final String status;

    public Agent(String id, String name, String model, String systemPrompt, String status) {
        this.id = id;
        this.name = name;
        this.model = model;
        this.systemPrompt = systemPrompt;
        this.status = status;
    }

    public String getId() { return id; }
    public String getName() { return name; }
    public String getModel() { return model; }
    public String getSystemPrompt() { return systemPrompt; }
    public String getStatus() { return status; }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Agent agent = (Agent) o;
        return Objects.equals(id, agent.id);
    }

    @Override
    public int hashCode() {
        return Objects.hash(id);
    }

    @Override
    public String toString() {
        return "Agent{id='" + id + "', name='" + name + "', model='" + model + "'}";
    }
}
