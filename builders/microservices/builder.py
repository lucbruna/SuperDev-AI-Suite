"""Microservices Builder — generates microservices project scaffolding with service discovery."""

from __future__ import annotations

import json
import time
from typing import Any

from ..base import (
    ApiType, BaseBuilder, BuildConfig, BuildResult, DatabaseType,
    FrameworkType, GeneratedFile,
)


class MicroservicesBuilder(BaseBuilder):
    name = "microservices"
    description = "Generates multi-service microservices project with Docker Compose orchestration"
    framework = FrameworkType.FASTAPI

    SERVICE_TEMPLATES = {
        "auth": {
            "port": 8001,
            "description": "Authentication and authorization service",
            "deps": ["python-jose[cryptography]", "passlib[bcrypt]", "asyncpg"],
            "db": True,
        },
        "users": {
            "port": 8002,
            "description": "User management service",
            "deps": ["asyncpg"],
            "db": True,
        },
        "api-gateway": {
            "port": 8000,
            "description": "API Gateway / reverse proxy",
            "deps": ["httpx"],
            "db": False,
        },
        "notifications": {
            "port": 8003,
            "description": "Email and push notification service",
            "deps": ["httpx", "smtplib"],
            "db": False,
        },
    }

    async def build(self, config: BuildConfig) -> BuildResult:
        start = time.time()
        slug = config.project_slug
        files: list[GeneratedFile] = []

        try:
            services = config.extra_config.get("services", list(self.SERVICE_TEMPLATES.keys()))

            # Root project files
            files.extend(self._generate_root_files(config, slug, services))

            # Per-service files
            for service_name in services:
                template = self.SERVICE_TEMPLATES.get(service_name, {
                    "port": 8100 + services.index(service_name),
                    "description": f"{service_name} service",
                    "deps": [],
                    "db": False,
                })
                files.extend(self._generate_service(service_name, template, config, slug))

            elapsed_ms = round((time.time() - start) * 1000, 2)
            return BuildResult(
                builder_name=self.name,
                project_name=config.project_name,
                project_slug=slug,
                total_files=len(files),
                files=files,
                build_duration_ms=elapsed_ms,
            )
        except Exception as e:
            return BuildResult(
                builder_name=self.name,
                project_name=config.project_name,
                project_slug=slug,
                error=str(e),
                build_duration_ms=round((time.time() - start) * 1000, 2),
            )

    def _generate_root_files(
        self, config: BuildConfig, slug: str, services: list[str],
    ) -> list[GeneratedFile]:
        files: list[GeneratedFile] = []

        # docker-compose.yml
        services_yml: dict[str, Any] = {
            "version": "3.9",
            "services": {},
            "networks": {"microservices": {"driver": "bridge"}},
        }

        for svc in services:
            template = self.SERVICE_TEMPLATES.get(svc, {"port": 8000, "db": False})
            port = template["port"]
            svc_config = {
                "build": f"./services/{svc}",
                "ports": [f"{port}:{port}"],
                "environment": [f"SERVICE_NAME={svc}", f"SERVICE_PORT={port}"],
                "networks": ["microservices"],
                "restart": "unless-stopped",
            }
            if template["db"]:
                db_svc = f"{svc}-db"
                services_yml["services"][db_svc] = {
                    "image": "postgres:16-alpine",
                    "environment": [
                        f"POSTGRES_DB={svc}",
                        "POSTGRES_USER=postgres",
                        "POSTGRES_PASSWORD=postgres",
                    ],
                    "networks": ["microservices"],
                    "volumes": [f"{db_svc}-data:/var/lib/postgresql/data"],
                }
                svc_config["environment"].append(f"DATABASE_URL=postgresql+asyncpg://postgres:postgres@{db_svc}:5432/{svc}")
                svc_config["depends_on"] = [db_svc]
                services_yml["volumes"] = {f"{db_svc}-data": None}

            services_yml["services"][svc] = svc_config

        # Try to use PyYAML if available, fall back to simple serializer
        try:
            import yaml
            yaml_str = yaml.dump(services_yml, default_flow_style=False, sort_keys=False)
        except ImportError:
            yaml_str = self._yaml_dump(services_yml)
        files.append(self._make_file(
            f"{slug}/docker-compose.yml",
            yaml_str,
            language="yaml",
        ))

        # .env.example
        env_vars = []
        for svc in services:
            env_vars.append(f"# {svc}")
            env_vars.append(f"{svc.upper().replace('-', '_')}_PORT={self.SERVICE_TEMPLATES.get(svc, {}).get('port', 8000)}")
        files.append(self._make_file(
            f"{slug}/.env.example",
            "\n".join(env_vars) + "\n",
            language="ini",
        ))

        # README.md
        svc_list = "\n".join(f"- **{s}** (port {self.SERVICE_TEMPLATES.get(s, {}).get('port', '?')})" for s in services)
        files.append(self._make_file(
            f"{slug}/README.md",
            f'''# {config.project_name}

Microservices project with {len(services)} services.

## Services

{svc_list}

## Quick Start

```bash
docker compose up -d --build
```
''',
            language="markdown",
        ))

        # .gitignore
        files.append(self._make_file(
            f"{slug}/.gitignore",
            "__pycache__/\n.env\n*.pyc\n.venv/\n",
            language="ini",
        ))

        # API Gateway configuration (if present) — parametrized with actual services
        if "api-gateway" in services:
            gateway_services = [
                f'        {{"name": "{s}", "port": {self.SERVICE_TEMPLATES.get(s, {}).get("port", 8000)}}}'
                for s in services if s != "api-gateway"
            ]
            gateway_service_list = "\n".join(gateway_services)
            files.append(self._make_file(
                f"{slug}/services/api-gateway/main.py",
                f'''"""API Gateway — routes requests to the appropriate microservice."""

from __future__ import annotations

import httpx
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

app = FastAPI(title="{config.project_name} API Gateway")

SERVICE_MAP = {{
    service["name"]: f"http://{{service['name']}}:{{service['port']}}"
    for service in [
{gateway_service_list}
    ]
}}


@app.get("/")
async def root() -> dict[str, str]:
    return {{"message": "API Gateway", "services": list(SERVICE_MAP.keys())}}


@app.get("/health")
async def health() -> dict[str, str]:
    return {{"status": "healthy"}}


@app.api_route("/{{path:path}}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy(request: Request, path: str) -> Response:
    service_name = path.split("/")[0] if "/" in path else path
    target = SERVICE_MAP.get(service_name)
    if not target:
        return JSONResponse({{"detail": "Service not found"}}, status_code=404)
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.request(
                method=request.method,
                url=f"{{target}}/{{'/'.join(path.split('/')[1:])}}",
                headers={{k: v for k, v in request.headers.items() if k != "host"}},
            )
            return Response(content=resp.content, status_code=resp.status_code)
        except httpx.RequestError:
            return JSONResponse({{"detail": "Service unavailable"}}, status_code=503)
''',
                language="python",
            ))

        return files

    def _generate_service(
        self, name: str, template: dict, config: BuildConfig, slug: str,
    ) -> list[GeneratedFile]:
        files: list[GeneratedFile] = []
        port = template["port"]
        svc_slug = name.replace("-", "_")
        svc_dir = f"{slug}/services/{name}"

        # main.py
        files.append(self._make_file(
            f"{svc_dir}/main.py",
            f'''"""{template["description"]}."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="{name}", version="1.0.0", docs_url="/docs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root() -> dict[str, str]:
    return {{"service": "{name}", "status": "running"}}


@app.get("/health")
async def health() -> dict[str, str]:
    return {{"status": "healthy"}}
''',
            language="python",
        ))

        # requirements.txt
        deps = ["fastapi>=0.110.0", "uvicorn[standard]>=0.27.0", "pydantic>=2.5.0"]
        deps.extend(template.get("deps", []))
        if template.get("db"):
            deps.extend(["sqlalchemy[asyncio]>=2.0.25", "asyncpg>=0.29.0"])
        files.append(self._make_file(
            f"{svc_dir}/requirements.txt",
            "\n".join(deps) + "\n",
            language="ini",
        ))

        # Dockerfile
        files.append(self._make_file(
            f"{svc_dir}/Dockerfile",
            f'''FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE {port}
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "{port}"]
''',
            language="dockerfile",
        ))

        # config.py (if has DB)
        if template.get("db"):
            db_url = f"postgresql+asyncpg://postgres:postgres@localhost:5432/{svc_slug}"
            files.append(self._make_file(
                f"{svc_dir}/config.py",
                f'''"""Service configuration."""

from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    service_name: str = "{name}"
    service_port: int = {port}
    database_url: str = "{db_url}"
    debug: bool = False

    class Config:
        env_file = ".env"


settings = Settings()
''',
                language="python",
            ))

            # models.py
            files.append(self._make_file(
                f"{svc_dir}/models.py",
                '''"""Database models."""

from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
''',
                language="python",
            ))

        return files

    @staticmethod
    def _yaml_dump(data: dict, indent: int = 0) -> str:
        """Simple YAML serializer (no PyYAML dependency needed)."""
        lines: list[str] = []
        for key, value in data.items():
            prefix = "  " * indent
            if isinstance(value, dict):
                lines.append(f"{prefix}{key}:")
                lines.append(MicroservicesBuilder._yaml_dump(value, indent + 1))
            elif isinstance(value, list):
                lines.append(f"{prefix}{key}:")
                for item in value:
                    if isinstance(item, dict):
                        for k, v in item.items():
                            lines.append(f"{prefix}  {k}: {v}")
                    else:
                        lines.append(f"{prefix}  - {item}")
            elif isinstance(value, bool):
                lines.append(f"{prefix}{key}: {'true' if value else 'false'}")
            elif value is None:
                lines.append(f"{prefix}{key}:")
            else:
                lines.append(f"{prefix}{key}: {value}")
        return "\n".join(lines) + "\n"
