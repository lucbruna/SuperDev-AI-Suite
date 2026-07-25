package com.superdev.sdk.types;

import java.util.Objects;

/**
 * Represents a chat response from an AI agent.
 */
public final class ChatResponse {
    private final String id;
    private final String content;
    private final String role;
    private final int tokensUsed;
    private final long createdAt;

    public ChatResponse(String id, String content, String role, int tokensUsed, long createdAt) {
        this.id = id;
        this.content = content;
        this.role = role;
        this.tokensUsed = tokensUsed;
        this.createdAt = createdAt;
    }

    public String getId() { return id; }
    public String getContent() { return content; }
    public String getRole() { return role; }
    public int getTokensUsed() { return tokensUsed; }
    public long getCreatedAt() { return createdAt; }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        ChatResponse that = (ChatResponse) o;
        return Objects.equals(id, that.id);
    }

    @Override
    public int hashCode() {
        return Objects.hash(id);
    }

    @Override
    public String toString() {
        return "ChatResponse{id='" + id + "', role='" + role + "', tokensUsed=" + tokensUsed + "}";
    }
}
