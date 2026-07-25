package com.superdev.sdk.types;

import java.util.Objects;

/**
 * Represents a plugin in the SuperDev system.
 */
public final class Plugin {
    private final String id;
    private final String name;
    private final String description;
    private final String version;
    private final String author;

    public Plugin(String id, String name, String description, String version, String author) {
        this.id = id;
        this.name = name;
        this.description = description;
        this.version = version;
        this.author = author;
    }

    public String getId() { return id; }
    public String getName() { return name; }
    public String getDescription() { return description; }
    public String getVersion() { return version; }
    public String getAuthor() { return author; }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Plugin plugin = (Plugin) o;
        return Objects.equals(id, plugin.id);
    }

    @Override
    public int hashCode() {
        return Objects.hash(id);
    }

    @Override
    public String toString() {
        return "Plugin{id='" + id + "', name='" + name + "', version='" + version + "'}";
    }
}
