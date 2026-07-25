package com.superdev.sdk.types;

import java.util.Objects;

/**
 * Represents an AI provider in the SuperDev system.
 */
public final class Provider {
    private final String id;
    private final String name;
    private final String type;
    private final boolean enabled;

    public Provider(String id, String name, String type, boolean enabled) {
        this.id = id;
        this.name = name;
        this.type = type;
        this.enabled = enabled;
    }

    public String getId() { return id; }
    public String getName() { return name; }
    public String getType() { return type; }
    public boolean isEnabled() { return enabled; }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Provider provider = (Provider) o;
        return Objects.equals(id, provider.id);
    }

    @Override
    public int hashCode() {
        return Objects.hash(id);
    }

    @Override
    public String toString() {
        return "Provider{id='" + id + "', name='" + name + "', type='" + type + "'}";
    }
}
