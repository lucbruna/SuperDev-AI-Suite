"""Backend Builder — generates FastAPI/Django/Flask project scaffolding."""

from __future__ import annotations

import time

from ..base import (
    BaseBuilder,
    BuildConfig,
    BuildResult,
    DatabaseType,
    FrameworkType,
    GeneratedFile,
)


class BackendBuilder(BaseBuilder):
    name = "backend"
    description = "Generates backend project scaffolding (FastAPI, Django, Flask)"
    framework = FrameworkType.FASTAPI

    async def build(self, config: BuildConfig) -> BuildResult:
        start = time.time()
        files: list[GeneratedFile] = []
        slug = config.project_slug

        try:
            if config.framework == FrameworkType.FASTAPI:
                files = self._generate_fastapi(config, slug)
            elif config.framework == FrameworkType.DJANGO:
                files = self._generate_django(config, slug)
            elif config.framework == FrameworkType.FLASK:
                files = self._generate_flask(config, slug)
            else:
                files = self._generate_python(config, slug)

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

    def _generate_fastapi(self, config: BuildConfig, slug: str) -> list[GeneratedFile]:
        files: list[GeneratedFile] = []
        db_dsn = {
            DatabaseType.POSTGRESQL: f"postgresql+asyncpg://postgres:postgres@localhost:5432/{slug}",
            DatabaseType.MYSQL: f"mysql+aiomysql://root:root@localhost:3306/{slug}",
            DatabaseType.SQLITE: f"sqlite+aiosqlite:///./{slug}.db",
        }.get(config.database, "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres")

        # main.py
        files.append(self._make_file(
            f"{slug}/main.py",
            f'''"""FastAPI application entry point."""

from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="{config.project_name}",
    version="1.0.0",
    docs_url="/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root() -> dict[str, str]:
    return {{"message": "{config.project_name} API", "version": "1.0.0"}}


@app.get("/health")
async def health() -> dict[str, str]:
    return {{"status": "healthy"}}
''',
            language="python",
        ))

        # config.py
        files.append(self._make_file(
            f"{slug}/config.py",
            f'''"""Application configuration."""

from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "{config.project_name}"
    debug: bool = False
    database_url: str = "{db_dsn}"
    secret_key: str = "change-me-in-production"
    allowed_hosts: list[str] = ["*"]

    class Config:
        env_file = ".env"


settings = Settings()
''',
            language="python",
        ))

        # models.py
        files.append(self._make_file(
            f"{slug}/models.py",
            '''"""SQLAlchemy database models."""

from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    name = Column(String(255))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
''',
            language="python",
        ))

        # schemas.py
        files.append(self._make_file(
            f"{slug}/schemas.py",
            '''"""Pydantic schemas for API request/response validation."""

from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    name: str


class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    created_at: datetime

    model_config = {"from_attributes": True}
''',
            language="python",
        ))

        # requirements.txt
        deps = [
            "fastapi>=0.110.0",
            "uvicorn[standard]>=0.27.0",
            "sqlalchemy[asyncio]>=2.0.25",
            "pydantic>=2.5.0",
            "pydantic-settings>=2.1.0",
            "pydantic[email]>=2.5.0",
        ]
        if config.database == DatabaseType.POSTGRESQL:
            deps.append("asyncpg>=0.29.0")
        elif config.database == DatabaseType.MYSQL:
            deps.append("aiomysql>=0.2.0")
        elif config.database == DatabaseType.SQLITE:
            deps.append("aiosqlite>=0.19.0")

        if config.include_auth:
            deps.extend(["python-jose[cryptography]>=3.3.0", "passlib[bcrypt]>=1.7.4"])
            files.append(self._make_file(
                f"{slug}/auth.py",
                '''"""JWT authentication utilities."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "change-me"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
''',
                language="python",
            ))

        if config.include_docker:
            files.append(self._make_file(
                f"{slug}/Dockerfile",
                f'''FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "{slug}.main:app", "--host", "0.0.0.0", "--port", "8000"]
''',
                language="dockerfile",
            ))
            files.append(self._make_file(
                f"{slug}/docker-compose.yml",
                f'''version: "3.9"

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL={db_dsn}
    volumes:
      - .:/app
''',
                language="yaml",
            ))

        if config.include_tests:
            files.append(self._make_file(
                f"{slug}/tests/__init__.py",
                "",
                language="python",
            ))
            files.append(self._make_file(
                f"{slug}/tests/test_main.py",
                f'''"""Tests for the API endpoints."""

from fastapi.testclient import TestClient
from {slug}.main import app

client = TestClient(app)


def test_root() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "{config.project_name} API"


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
''',
                language="python",
            ))

        if config.include_ci:
            files.append(self._make_file(
                f"{slug}/.github/workflows/ci.yml",
                '''name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r requirements.txt
      - run: pip install pytest httpx
      - run: pytest
''',
                language="yaml",
            ))

        # .env.example
        files.append(self._make_file(
            f"{slug}/.env.example",
            f'''APP_NAME="{config.project_name}"
DEBUG=false
DATABASE_URL={db_dsn}
SECRET_KEY=change-me-in-production
''',
            language="ini",
        ))

        # .gitignore
        files.append(self._make_file(
            f"{slug}/.gitignore",
            '''__pycache__/
*.py[cod]
*.egg-info/
.env
venv/
.venv/
dist/
build/
''',
            language="ini",
        ))

        # README.md
        files.append(self._make_file(
            f"{slug}/README.md",
            f'''# {config.project_name}

Backend API built with {config.framework.value}.

## Quick Start

```bash
pip install -r requirements.txt
uvicorn {slug}.main:app --reload
```

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
''',
            language="markdown",
        ))

        return files

    def _generate_django(self, config: BuildConfig, slug: str) -> list[GeneratedFile]:
        """Generate Django project scaffolding."""
        files: list[GeneratedFile] = []

        files.append(self._make_file(
            f"{slug}/manage.py",
            f'''#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "{slug}.settings")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
''',
            language="python",
        ))

        files.append(self._make_file(
            f"{slug}/{slug}/settings.py",
            f'''"""Django settings."""
from pathlib import Path

import os

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split(",")
DATABASES = {{
    "default": {{
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "{slug}",
        "USER": "postgres",
        "PASSWORD": "postgres",
        "HOST": "localhost",
        "PORT": "5432",
    }}
}}
INSTALLED_APPS = [
    "django.contrib.admin", "django.contrib.auth",
    "django.contrib.contenttypes", "django.contrib.sessions",
    "django.contrib.messages", "django.contrib.staticfiles",
    "rest_framework",
]
ROOT_URLCONF = "{slug}.urls"
''',
            language="python",
        ))

        # urls.py
        files.append(self._make_file(
            f"{slug}/{slug}/urls.py",
            '''"""URL configuration."""

from django.contrib import admin
from django.urls import path

urlpatterns = [
    path("admin/", admin.site.urls),
]
''',
            language="python",
        ))

        files.append(self._make_file(
            f"{slug}/requirements.txt",
            "django>=5.0\ndjangorestframework>=3.14.0\npsycopg2-binary>=2.9.0\n",
            language="ini",
        ))

        if config.include_docker:
            files.append(self._make_file(
                f"{slug}/Dockerfile",
                '''FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
''',
                language="dockerfile",
            ))

        files.append(self._make_file(
            f"{slug}/.gitignore",
            "__pycache__/\n*.pyc\n*.pyo\n.env\ndb.sqlite3\n",
            language="ini",
        ))

        return files

    def _generate_flask(self, config: BuildConfig, slug: str) -> list[GeneratedFile]:
        """Generate Flask project scaffolding."""
        files: list[GeneratedFile] = []

        files.append(self._make_file(
            f"{slug}/app.py",
            f'''"""Flask application entry point."""
import os

from flask import Flask, jsonify

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "change-me-in-production")


@app.route("/")
def root():
    return jsonify({{"message": "{config.project_name}", "version": "1.0.0"}})


@app.route("/health")
def health():
    return jsonify({{"status": "healthy"}})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=os.getenv("DEBUG", "false").lower() == "true")
''',
            language="python",
        ))

        files.append(self._make_file(
            f"{slug}/requirements.txt",
            "flask>=3.0\nflask-sqlalchemy>=3.1\n",
            language="ini",
        ))

        if config.include_docker:
            files.append(self._make_file(
                f"{slug}/Dockerfile",
                '''FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
''',
                language="dockerfile",
            ))

        files.append(self._make_file(
            f"{slug}/.gitignore",
            "__pycache__/\n*.pyc\n.env\ninstance/\n",
            language="ini",
        ))

        return files

    def _generate_python(self, config: BuildConfig, slug: str) -> list[GeneratedFile]:
        """Generate generic Python package scaffolding."""
        files: list[GeneratedFile] = []

        files.append(self._make_file(
            f"{slug}/__init__.py",
            f'"""_{config.project_name}_ package."""\n\n__version__ = "0.1.0"\n',
            language="python",
        ))

        files.append(self._make_file(
            f"{slug}/cli.py",
            f'''"""CLI entry point."""
import argparse


def main():
    parser = argparse.ArgumentParser(description="{config.project_name}")
    parser.add_argument("--version", action="store_true", help="Show version")
    args = parser.parse_args()
    if args.version:
        from {slug} import __version__
        print(f"{{__version__}}")


if __name__ == "__main__":
    main()
''',
            language="python",
        ))

        files.append(self._make_file(
            f"{slug}/pyproject.toml",
            f'''[build-system]
requires = ["setuptools>=68.0"]
build-backend = "setuptools.build_meta"

[project]
name = "{slug}"
version = "0.1.0"
description = "{config.project_name}"
requires-python = ">=3.11"
''',
            language="toml",
        ))

        return files
