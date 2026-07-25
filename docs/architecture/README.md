# Architecture

SuperDev AI Suite v5.0 is a modular, enterprise-grade AI development platform.

## Overview

- **Backend**: Python (FastAPI) with SQLAlchemy, Redis, PostgreSQL
- **Frontend**: React + Next.js + TypeScript + Tailwind CSS
- **CLI**: Python (Click/Typer)
- **SDKs**: Python, TypeScript, Go, Java, Rust, C#
- **Infrastructure**: Docker, Kubernetes, Terraform, Ansible

## Modules

| Module | Description | Path |
|--------|-------------|------|
| Backend | API, Auth, Database, Services | `backend/` |
| Frontend | Web UI, Dashboard, IDE | `frontend/` |
| CLI | Command line interface | `cli/` |
| Agents | AI agent platform | `agents/` |
| AI Platform | Provider routing, streaming | `ai_platform/` |
| Workflow Engine | DAG-based workflows | `workflow_engine/` |
| Runtime Engine | Sandboxed execution | `runtime_engine/` |
| Plugin Platform | Marketplace, sandboxing | `plugin_platform/` |
| Enterprise | SSO, billing, multi-tenancy | `enterprise/` |

## Data Flow

```
User → Frontend → API Gateway → Backend Services
                                    ↓
                              AI Router → Providers (OpenAI, Anthropic, etc.)
                                    ↓
                              Workflow Engine → Runtime Engine → Sandbox
                                    ↓
                              Database (PostgreSQL) + Cache (Redis)
```
