from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum


class AgentTier(Enum):
    """Agent hierarchy tiers."""
    SUPER_ORCHESTRATOR = 0
    DOMAIN_MANAGER = 1
    SPECIALIST = 2
    EXECUTOR = 3
    TOOL = 4


class AgentCapability(Enum):
    """Standard agent capabilities."""
    CHAT = "chat"
    STREAM = "stream"
    EMBEDDINGS = "embeddings"
    VISION = "vision"
    TOOLS = "tools"
    CODE_EXECUTION = "code_execution"
    PLANNING = "planning"
    REASONING = "reasoning"
    MEMORY = "memory"
    LEARNING = "learning"


@dataclass
class ModelConfig:
    """Model configuration for an agent."""
    provider: str = "openai"
    model: str = "gpt-4o"
    temperature: float = 0.7
    max_tokens: int = 4096
    timeout: int = 120
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop_sequences: List[str] = field(default_factory=list)


@dataclass
class ToolConfig:
    """Tool configuration for an agent."""
    name: str
    enabled: bool = True
    config: Dict[str, Any] = field(default_factory=dict)
    permissions: List[str] = field(default_factory=list)


@dataclass
class MemoryConfig:
    """Memory configuration for an agent."""
    short_term_size: int = 100
    long_term_enabled: bool = True
    vector_memory_enabled: bool = False
    embedding_model: str = "text-embedding-3-small"
    memory_ttl_hours: int = 168  # 1 week


@dataclass
class LearningConfig:
    """Learning configuration for an agent."""
    enabled: bool = False
    feedback_enabled: bool = True
    reinforcement_enabled: bool = False
    adaptation_rate: float = 0.1
    experience_retention_days: int = 30


@dataclass
class AgentConfig:
    """Complete configuration for an agent."""
    # Identity
    agent_id: str
    name: str
    agent_type: str
    tier: AgentTier = AgentTier.SPECIALIST
    description: str = ""
    
    # Model
    model: ModelConfig = field(default_factory=ModelConfig)
    
    # Capabilities
    capabilities: List[AgentCapability] = field(default_factory=list)
    tools: List[ToolConfig] = field(default_factory=list)
    
    # Memory
    memory: MemoryConfig = field(default_factory=MemoryConfig)
    
    # Learning
    learning: LearningConfig = field(default_factory=LearningConfig)
    
    # Behavior
    instructions: str = ""
    system_prompt: str = ""
    personality_traits: Dict[str, float] = field(default_factory=dict)
    constraints: List[str] = field(default_factory=list)
    
    # Execution
    max_iterations: int = 10
    max_execution_time: int = 300
    parallel_execution: bool = False
    
    # Monitoring
    enable_metrics: bool = True
    enable_logging: bool = True
    log_level: str = "INFO"
    
    # Security
    permissions: List[str] = field(default_factory=list)
    allowed_domains: List[str] = field(default_factory=list)
    blocked_domains: List[str] = field(default_factory=list)
    
    # Metadata
    tags: List[str] = field(default_factory=list)
    version: str = "1.0.0"
    created_at: str = ""
    updated_at: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "agent_type": self.agent_type,
            "tier": self.tier.value,
            "description": self.description,
            "model": {
                "provider": self.model.provider,
                "model": self.model.model,
                "temperature": self.model.temperature,
                "max_tokens": self.model.max_tokens,
                "timeout": self.model.timeout,
                "top_p": self.model.top_p,
                "frequency_penalty": self.model.frequency_penalty,
                "presence_penalty": self.model.presence_penalty,
                "stop_sequences": self.model.stop_sequences,
            },
            "capabilities": [c.value for c in self.capabilities],
            "tools": [
                {
                    "name": t.name,
                    "enabled": t.enabled,
                    "config": t.config,
                    "permissions": t.permissions,
                }
                for t in self.tools
            ],
            "memory": {
                "short_term_size": self.memory.short_term_size,
                "long_term_enabled": self.memory.long_term_enabled,
                "vector_memory_enabled": self.memory.vector_memory_enabled,
                "embedding_model": self.memory.embedding_model,
                "memory_ttl_hours": self.memory.memory_ttl_hours,
            },
            "learning": {
                "enabled": self.learning.enabled,
                "feedback_enabled": self.learning.feedback_enabled,
                "reinforcement_enabled": self.learning.reinforcement_enabled,
                "adaptation_rate": self.learning.adaptation_rate,
                "experience_retention_days": self.learning.experience_retention_days,
            },
            "instructions": self.instructions,
            "system_prompt": self.system_prompt,
            "personality_traits": self.personality_traits,
            "constraints": self.constraints,
            "max_iterations": self.max_iterations,
            "max_execution_time": self.max_execution_time,
            "parallel_execution": self.parallel_execution,
            "enable_metrics": self.enable_metrics,
            "enable_logging": self.enable_logging,
            "log_level": self.log_level,
            "permissions": self.permissions,
            "allowed_domains": self.allowed_domains,
            "blocked_domains": self.blocked_domains,
            "tags": self.tags,
            "version": self.version,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentConfig":
        """Create from dictionary."""
        config = cls(
            agent_id=data.get("agent_id", ""),
            name=data.get("name", ""),
            agent_type=data.get("agent_type", ""),
            tier=AgentTier(data.get("tier", 2)),
            description=data.get("description", ""),
        )
        
        # Model
        model_data = data.get("model", {})
        config.model = ModelConfig(
            provider=model_data.get("provider", "openai"),
            model=model_data.get("model", "gpt-4o"),
            temperature=model_data.get("temperature", 0.7),
            max_tokens=model_data.get("max_tokens", 4096),
            timeout=model_data.get("timeout", 120),
            top_p=model_data.get("top_p", 1.0),
            frequency_penalty=model_data.get("frequency_penalty", 0.0),
            presence_penalty=model_data.get("presence_penalty", 0.0),
            stop_sequences=model_data.get("stop_sequences", []),
        )
        
        # Capabilities
        config.capabilities = [
            AgentCapability(c) for c in data.get("capabilities", [])
        ]
        
        # Tools
        config.tools = [
            ToolConfig(
                name=t.get("name", ""),
                enabled=t.get("enabled", True),
                config=t.get("config", {}),
                permissions=t.get("permissions", []),
            )
            for t in data.get("tools", [])
        ]
        
        # Memory
        mem_data = data.get("memory", {})
        config.memory = MemoryConfig(
            short_term_size=mem_data.get("short_term_size", 100),
            long_term_enabled=mem_data.get("long_term_enabled", True),
            vector_memory_enabled=mem_data.get("vector_memory_enabled", False),
            embedding_model=mem_data.get("embedding_model", "text-embedding-3-small"),
            memory_ttl_hours=mem_data.get("memory_ttl_hours", 168),
        )
        
        # Learning
        learn_data = data.get("learning", {})
        config.learning = LearningConfig(
            enabled=learn_data.get("enabled", False),
            feedback_enabled=learn_data.get("feedback_enabled", True),
            reinforcement_enabled=learn_data.get("reinforcement_enabled", False),
            adaptation_rate=learn_data.get("adaptation_rate", 0.1),
            experience_retention_days=learn_data.get("experience_retention_days", 30),
        )
        
        # Behavior
        config.instructions = data.get("instructions", "")
        config.system_prompt = data.get("system_prompt", "")
        config.personality_traits = data.get("personality_traits", {})
        config.constraints = data.get("constraints", [])
        
        # Execution
        config.max_iterations = data.get("max_iterations", 10)
        config.max_execution_time = data.get("max_execution_time", 300)
        config.parallel_execution = data.get("parallel_execution", False)
        
        # Monitoring
        config.enable_metrics = data.get("enable_metrics", True)
        config.enable_logging = data.get("enable_logging", True)
        config.log_level = data.get("log_level", "INFO")
        
        # Security
        config.permissions = data.get("permissions", [])
        config.allowed_domains = data.get("allowed_domains", [])
        config.blocked_domains = data.get("blocked_domains", [])
        
        # Metadata
        config.tags = data.get("tags", [])
        config.version = data.get("version", "1.0.0")
        config.created_at = data.get("created_at", "")
        config.updated_at = data.get("updated_at", "")
        config.metadata = data.get("metadata", {})
        
        return config


@dataclass
class TeamConfig:
    """Configuration for an agent team."""
    team_id: str
    name: str
    description: str = ""
    agent_ids: List[str] = field(default_factory=list)
    coordination_strategy: str = "hierarchical"
    shared_memory_enabled: bool = True
    communication_protocol: str = "message_bus"
    max_concurrent_tasks: int = 10
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OrchestrationConfig:
    """Global orchestration configuration."""
    max_agents: int = 100
    max_teams: int = 20
    default_timeout: int = 300
    health_check_interval: int = 30
    metrics_collection_interval: int = 60
    auto_scaling_enabled: bool = False
    cost_optimization_enabled: bool = True
    security_audit_enabled: bool = True