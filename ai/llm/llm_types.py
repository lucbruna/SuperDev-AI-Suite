from __future__ import annotations

from typing import Any, Literal

LLMProviderStatus = Literal["active", "inactive", "error", "degraded", "maintenance"]
LLMRouteStrategy = Literal[
    "capability", "latency", "cost", "quality", "availability", "weighted", "priority", "smart", "fallback"
]
LLMStreamEvent = Literal["start", "token", "end", "error", "cancel"]

ProviderName = str
ModelName = str
TokenCount = int
CostValue = float
LatencyMs = float
ConfidenceScore = float

ProviderConfig = dict[str, Any]
ModelConfig = dict[str, Any]
PromptTemplate = str
MessageList = list[dict[str, Any]]

LLMResult = dict[str, Any]
StreamChunk = dict[str, Any]
EmbeddingVector = list[float]
