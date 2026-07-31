from __future__ import annotations

from backend.settings import (
    AppSettings,
    AuthSettings,
    CorsSettings,
    DatabaseSettings,
    KnowledgeBaseSettings,
    LoggingSettings,
    PluginSettings,
    ProviderSettings,
    RedisSettings,
    SandboxSettings,
    TelemetrySettings,
    VerificationSettings,
    WorkflowSettings,
)
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore",
    )

    app: AppSettings = AppSettings()
    database: DatabaseSettings = DatabaseSettings()
    redis: RedisSettings = RedisSettings()
    auth: AuthSettings = AuthSettings()
    cors: CorsSettings = CorsSettings()
    logging: LoggingSettings = LoggingSettings()
    telemetry: TelemetrySettings = TelemetrySettings()
    providers: ProviderSettings = ProviderSettings()
    sandbox: SandboxSettings = SandboxSettings()
    knowledge_base: KnowledgeBaseSettings = KnowledgeBaseSettings()
    plugins: PluginSettings = PluginSettings()
    workflow: WorkflowSettings = WorkflowSettings()
    verification: VerificationSettings = VerificationSettings()


config: AppConfig = AppConfig()

# Alias for backward compatibility
settings = config