package com.superdev.sdk.types;

import java.util.Objects;

/**
 * Represents a chunk of a streaming response.
 */
public final class StreamingChunk {
    private final String id;
    private final String delta;
    private final boolean finished;
    private final int tokensUsed;

    public StreamingChunk(String id, String delta, boolean finished, int tokensUsed) {
        this.id = id;
        this.delta = delta;
        this.finished = finished;
        this.tokensUsed = tokensUsed;
    }

    public String getId() { return id; }
    public String getDelta() { return delta; }
    public boolean isFinished() { return finished; }
    public int getTokensUsed() { return tokensUsed; }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        StreamingChunk that = (StreamingChunk) o;
        return Objects.equals(id, that.id);
    }

    @Override
    public int hashCode() {
        return Objects.hash(id);
    }

    @Override
    public String toString() {
        return "StreamingChunk{id='" + id + "', finished=" + finished + "}";
    }
}
