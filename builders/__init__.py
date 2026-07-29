"""SuperDev Builders — project scaffolding and code generation modules.

Builders generate complete project scaffolding for various frameworks,
platforms, and architectures including backend APIs, frontend apps,
microservices, and more.

Modules:
    base              — Base classes, types, and configuration models
    backend           — Backend project generator (FastAPI, Django, Flask)
    frontend          — Frontend project generator (React, Next.js, Vue, Svelte)
    api               — API scaffolding generator (REST, GraphQL, WebSocket, gRPC)
    microservices     — Microservices project generator with Docker Compose
"""

from .base import (
    ApiType, BaseBuilder, BuildConfig, BuildResult,
    DatabaseType, FrameworkType, GeneratedFile,
)
from .backend.builder import BackendBuilder
from .frontend.builder import FrontendBuilder
from .api.builder import APIBuilder
from .microservices.builder import MicroservicesBuilder

__all__ = [
    # Types
    "ApiType", "BaseBuilder", "BuildConfig", "BuildResult",
    "DatabaseType", "FrameworkType", "GeneratedFile",
    # Builders
    "BackendBuilder", "FrontendBuilder", "APIBuilder", "MicroservicesBuilder",
]
