"""Factory Models - Data models for software factory."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class Language(Enum):
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    GO = "go"
    RUST = "rust"
    CSHARP = "csharp"
    SWIFT = "swift"
    KOTLIN = "kotlin"


class ArchitecturePattern(Enum):
    MONOLITH = "monolith"
    MICROSERVICES = "microservices"
    SERVERLESS = "serverless"
    EVENT_DRIVEN = "event_driven"
    MVC = "mvc"


class DatabaseType(Enum):
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLITE = "sqlite"
    MONGODB = "mongodb"
    REDIS = "redis"


@dataclass
class TechStack:
    language: Language = Language.PYTHON
    framework: str = ""
    database: DatabaseType = DatabaseType.POSTGRESQL
    architecture: ArchitecturePattern = ArchitecturePattern.MONOLITH
    frontend: str = ""
    deployment: str = ""
    testing: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CodeFile:
    file_id: str
    path: str
    language: Language = Language.PYTHON
    content: str = ""
    lines: int = 0
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class DatabaseSchema:
    schema_id: str
    name: str
    tables: list[dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class TestSuite:
    suite_id: str
    project_id: str
    name: str = ""
    tests: list[dict[str, Any]] = field(default_factory=list)
    passed: int = 0
    failed: int = 0
    total: int = 0
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class DeploymentConfig:
    deploy_id: str
    project_id: str
    target: str = ""
    method: str = "docker"
    environment: str = "production"
    config: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
