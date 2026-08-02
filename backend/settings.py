from __future__ import annotations

import json
from typing import Annotated, Any

from pydantic import BeforeValidator, Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


def _parse_str_list(value: Any) -> list[str]:
    """Parse a list[str] setting read from env.

    Accepts both JSON arrays (``["a", "b"]``) and comma-separated strings
    (``a,b``), plus a single bare value (``*``) or an empty value.
    """
    if isinstance(value, list):
        return [str(item) for item in value]
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return []
        if text.startswith("["):
            try:
                parsed = json.loads(text)
                if isinstance(parsed, list):
                    return [str(item) for item in parsed]
            except json.JSONDecodeError:
                pass  # not JSON → fall back to comma-separated parsing
        return [item.strip() for item in text.split(",") if item.strip()]
    return []


# list[str] settings read from env. NoDecode stops pydantic-settings from
# forcing JSON parsing (which rejects comma-separated .env values like
# CORS_ALLOW_METHODS=GET,POST,...); the BeforeValidator then accepts both
# JSON arrays and comma-separated strings.
StrList = Annotated[list[str], NoDecode, BeforeValidator(_parse_str_list)]


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="APP_",
        extra="ignore",
    )

    name: str = "SuperDev AI Suite"
    version: str = "6.0.0"
    environment: str = "development"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1
    log_level: str = "INFO"
    api_prefix: str = "/api/v1"
    docs_url: str = "/docs"
    openapi_url: str = "/openapi.json"
    root_path: str = ""
    max_request_size: int = 10_000_000
    request_timeout: int = 120


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="DATABASE_",
        extra="ignore",
    )

    url: str = "postgresql+asyncpg://superdev:superdev@localhost:5432/superdev"
    migration_dir: str = "backend/database/migrations"
    readonly_url: str = ""
    pool_size: int = 20
    max_overflow: int = 30
    pool_timeout: int = 30
    pool_recycle: int = 3600
    pool_pre_ping: bool = True
    echo: bool = False
    connect_timeout: int = 10
    statement_timeout: int = 30000
    idle_in_transaction_timeout: int = 60000
    lock_timeout: int = 10000
    # PgBouncer
    pgbouncer_url: str = ""
    pgbouncer_pool_mode: str = "transaction"


class RedisSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="REDIS_",
        extra="ignore",
    )

    host: str = "localhost"
    port: int = 6379
    password: str = ""
    db: int = 0
    decode_responses: bool = True
    max_connections: int = 50
    socket_timeout: float = 5.0
    socket_connect_timeout: float = 5.0
    socket_keepalive: bool = True
    retry_on_timeout: bool = True
    health_check_interval: int = 30
    # Sentinel
    sentinel_enabled: bool = False
    sentinel_hosts: StrList = []
    sentinel_password: str = ""
    service_name: str = "mymaster"
    # Cluster
    cluster_enabled: bool = False
    cluster_nodes: StrList = []

    @property
    def url(self) -> str:
        if self.password:
            return f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"
        return f"redis://{self.host}:{self.port}/{self.db}"

    # Replicas
    replica_hosts: StrList = []


# Known placeholder secrets that must never be used in real environments.
# jwt.py independently rejects these at token-manager creation time; this
# validator is defense-in-depth at the settings layer.
_INSECURE_SECRET_KEYS = {
    "change-me-in-production",
    "change-me-to-a-random-256-bit-secret",
    "super-dev-secret-key-change-in-production",
    "change-me",
}


class AuthSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="JWT_",
        extra="ignore",
    )

    # Empty by default on purpose: no known-insecure fallback. Auth endpoints
    # fail fast via jwt.py when the key is missing/placeholder.
    secret_key: str = Field(default="", exclude=True)
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    issuer: str = "superdev"
    audience: str = "superdev-api"
    bcrypt_rounds: int = 12
    # OAuth2/OIDC
    oauth2_enabled: bool = True
    oidc_enabled: bool = False
    oidc_issuer_url: str = ""
    oidc_client_id: str = ""
    oidc_client_secret: str = ""
    oidc_redirect_uri: str = "http://localhost:8000/api/v1/auth/callback"
    oidc_scopes: str = "openid,profile,email"
    # GitHub OAuth
    github_oauth_enabled: bool = False
    github_client_id: str = ""
    github_client_secret: str = ""
    # Google OAuth
    google_oauth_enabled: bool = False
    google_client_id: str = ""
    google_client_secret: str = ""
    # Session
    session_ttl_seconds: int = 3600
    session_cookie_name: str = "superdev_session"
    session_cookie_secure: bool = True
    session_cookie_httponly: bool = True
    session_cookie_samesite: str = "lax"

    @field_validator("secret_key")
    @classmethod
    def _reject_insecure_secret_key(cls, v: str) -> str:
        if v and v in _INSECURE_SECRET_KEYS:
            raise ValueError(
                "JWT_SECRET_KEY must be set to a strong, unique value. "
                "Known placeholder keys are rejected for security."
            )
        return v


class CorsSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="CORS_",
        extra="ignore",
    )

    allow_origins: StrList = ["http://localhost:3000", "http://localhost:8000"]
    allow_credentials: bool = True
    allow_methods: StrList = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
    allow_headers: StrList = ["*"]
    expose_headers: StrList = ["X-Request-ID", "X-Process-Time"]
    max_age: int = 3600


class LoggingSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="LOG_",
        extra="ignore",
    )

    level: str = "INFO"
    format: str = "json"
    output: str = "stdout"
    file_path: str = ""
    max_bytes: int = 10_485_760
    backup_count: int = 5
    correlation_id_header: str = "X-Request-ID"
    access_log: bool = True
    sql_log: bool = False


class TelemetrySettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="OTEL_",
        extra="ignore",
    )

    enabled: bool = True
    traces_enabled: bool = True
    metrics_enabled: bool = True
    service_name: str = "superdev-api"
    exporter_endpoint: str = "http://localhost:4318"
    traces_endpoint: str = ""
    metrics_endpoint: str = ""
    logs_endpoint: str = ""
    traces_sampler: str = "traceidratio"
    traces_sampler_arg: str = "0.1"
    resource_attributes: str = ""
    # Prometheus
    prometheus_enabled: bool = True
    prometheus_port: int = 9090
    prometheus_push_gateway: str = ""
    # Grafana
    grafana_enabled: bool = True
    grafana_url: str = "http://localhost:3000"
    grafana_api_key: str = ""
    # Jaeger
    jaeger_enabled: bool = True
    jaeger_agent_host: str = "localhost"
    jaeger_agent_port: int = 6831
    jaeger_collector_endpoint: str = "http://localhost:14268/api/traces"
    # Sentry
    sentry_dsn: str = ""
    sentry_environment: str = "development"
    sentry_traces_sample_rate: float = 0.1


class ProviderSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="",
        extra="ignore",
    )

    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    openai_base_url: str = "https://api.openai.com/v1"
    openai_organization: str = ""

    anthropic_api_key: str = ""
    anthropic_model: str = "claude-3-5-sonnet-20241022"
    anthropic_base_url: str = "https://api.anthropic.com"

    gemini_api_key: str = ""
    gemini_model: str = "gemini-1.5-pro"

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1"

    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"

    default_provider: str = "openai"
    routing_strategy: str = "auto"
    cost_max_per_1k: float = 0.10
    latency_max_ms: int = 5000

    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_dimension: int = 384
    embedding_batch_size: int = 32


class SandboxSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="RUNTIME_",
        extra="ignore",
    )

    sandbox_timeout: int = 300
    max_memory_mb: int = 512
    max_disk_mb: int = 1024
    max_cpu_seconds: int = 60
    max_processes: int = 50
    max_file_size_mb: int = 100
    enable_network: bool = False
    sandbox_image: str = "superdev-sandbox:latest"
    use_docker: bool = False
    docker_host: str = "unix:///var/run/docker.sock"
    seccomp_profile: str = "default"
    drop_capabilities: StrList = ["all"]
    use_user_namespace: bool = True
    uid_map: str = "0:100000:65536"
    gid_map: str = "0:100000:65536"


class KnowledgeBaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KB_",
        extra="ignore",
    )

    enabled: bool = True
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_dimension: int = 384
    chunk_size: int = 1000
    chunk_overlap: int = 200
    min_chunk_size: int = 100
    similarity_threshold: float = 0.5
    max_results: int = 10
    max_context_tokens: int = 8000


class PluginSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="PLUGIN_",
        extra="ignore",
    )

    enabled: bool = True
    plugin_dir: str = "./plugins"
    marketplace_url: str = "https://marketplace.superdev.ai/api/v1"
    marketplace_enabled: bool = True
    auto_update: bool = False
    sandbox_enabled: bool = True
    permissions_required: StrList = ["filesystem.read"]
    max_memory_mb: int = 256
    max_cpu_seconds: int = 30


class WorkflowSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="WORKFLOW_",
        extra="ignore",
    )

    enabled: bool = True
    max_concurrent: int = 10
    default_timeout: int = 3600
    max_retries: int = 3
    checkpoint_interval: int = 60
    state_ttl: int = 86400


class VerificationSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="VERIFICATION_",
        extra="ignore",
    )

    enabled: bool = True
    max_iterations: int = 3
    default_timeout: int = 300
    generation_temperature: float = 0.3
    review_temperature: float = 0.2
    correction_temperature: float = 0.1
    min_review_score: int = 70
    require_tests_pass: bool = True
    require_no_security_issues: bool = True
