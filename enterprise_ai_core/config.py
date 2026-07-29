"""
Configuration management for Enterprise AI Core
"""

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from pathlib import Path


@dataclass
class AgentConfig:
    name: str
    enabled: bool = True
    max_concurrent_tasks: int = 5
    timeout_seconds: int = 300
    retry_attempts: int = 3
    capabilities: List[str] = field(default_factory=list)
    permissions: List[str] = field(default_factory=list)
    config: Dict = field(default_factory=dict)


@dataclass
class WorkflowConfig:
    max_parallel_steps: int = 10
    default_timeout: int = 600
    retry_policy: Dict = field(default_factory=dict)
    checkpoint_enabled: bool = True


@dataclass
class PolicyConfig:
    enforcement_mode: str = "strict"
    rules_path: str = "policies/rules"
    auto_update: bool = True
    validation_interval: int = 3600


@dataclass
class MemoryConfig:
    short_term_ttl: int = 3600
    long_term_max_size: int = 10000
    vector_dimension: int = 1536
    embedding_model: str = "text-embedding-ada-002"
    cache_enabled: bool = True


@dataclass
class SecurityConfig:
    encryption_enabled: bool = True
    encryption_key: Optional[str] = None
    jwt_secret: Optional[str] = None
    token_expiry: int = 3600
    rate_limit: int = 100
    allowed_origins: List[str] = field(default_factory=lambda: ["*"])


@dataclass
class AuditConfig:
    log_level: str = "INFO"
    log_path: str = "logs/audit"
    retention_days: int = 90
    real_time_alerts: bool = True
    compliance_standards: List[str] = field(default_factory=lambda: ["SOC2", "GDPR"])


@dataclass
class MonitoringConfig:
    health_check_interval: int = 60
    metrics_retention: int = 86400
    alert_thresholds: Dict = field(default_factory=dict)
    tracing_enabled: bool = True


@dataclass
class Config:
    environment: str = "development"
    debug: bool = False
    agents: Dict[str, AgentConfig] = field(default_factory=dict)
    workflow: WorkflowConfig = field(default_factory=WorkflowConfig)
    policy: PolicyConfig = field(default_factory=PolicyConfig)
    memory: MemoryConfig = field(default_factory=MemoryConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    audit: AuditConfig = field(default_factory=AuditConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    database_url: str = "sqlite:///enterprise_ai.db"
    redis_url: str = "redis://localhost:6379/0"
    message_queue_url: str = "redis://localhost:6379/1"

    @classmethod
    def from_env(cls) -> "Config":
        config = cls()
        config.environment = os.getenv("ENVIRONMENT", "development")
        config.debug = os.getenv("DEBUG", "false").lower() == "true"
        config.database_url = os.getenv("DATABASE_URL", config.database_url)
        config.redis_url = os.getenv("REDIS_URL", config.redis_url)
        config.message_queue_url = os.getenv("MESSAGE_QUEUE_URL", config.message_queue_url)
        config.security.encryption_key = os.getenv("ENCRYPTION_KEY")
        config.security.jwt_secret = os.getenv("JWT_SECRET")
        return config

    def get_agent_config(self, name: str) -> Optional[AgentConfig]:
        return self.agents.get(name)

    def register_agent(self, agent_config: AgentConfig) -> None:
        self.agents[agent_config.name] = agent_config