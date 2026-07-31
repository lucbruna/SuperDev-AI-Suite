"""AI Model configuration."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ModelType(Enum):
    LLM = "llm"
    EMBEDDING = "embedding"
    VISION = "vision"
    AUDIO = "audio"
    MULTIMODAL = "multimodal"

class ProviderType(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    HUGGINGFACE = "huggingface"
    OLLAMA = "ollama"
    LOCAL = "local"
    CUSTOM = "custom"

class TaskType(Enum):
    CODING = "coding"
    REASONING = "reasoning"
    WRITING = "writing"
    ANALYSIS = "analysis"
    VISION = "vision"
    CONVERSATION = "conversation"
    TRANSLATION = "translation"
    SUMMARIZATION = "summarization"

@dataclass
class ModelLimits:
    max_tokens: int = 4096
    max_context: int = 128000
    max_batch_size: int = 32
    requests_per_minute: int = 60
    tokens_per_minute: int = 100000

@dataclass
class CostConfig:
    input_cost_per_1k: float = 0.01
    output_cost_per_1k: float = 0.03
    currency: str = "USD"
    budget_limit: float = 1000.0

@dataclass
class ModelConfig:
    limits: ModelLimits = field(default_factory=ModelLimits)
    cost: CostConfig = field(default_factory=CostConfig)
    default_provider: ProviderType = ProviderType.OPENAI
    fallback_enabled: bool = True
    cache_enabled: bool = True
    security_enabled: bool = True
    evaluation_enabled: bool = True
    debug_mode: bool = False
