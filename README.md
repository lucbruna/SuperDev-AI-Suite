# SuperDev AI Suite v5.0 Enterprise

**Enterprise-grade AI-powered development platform**

SuperDev AI Suite is a comprehensive, robust development platform that leverages artificial intelligence to accelerate software development workflows. From intelligent code generation to autonomous agent orchestration, SuperDev provides a unified runtime for building, testing, deploying, and monitoring modern applications at scale.

## Features

- **AI-Powered Code Generation** - Generate boilerplate, tests, documentation, and complete components using advanced LLM integration
- **Multi-Agent Orchestration** - Deploy and coordinate specialized AI agents for code review, debugging, refactoring, and optimization
- **Visual Workflow Editor** - Design complex CI/CD pipelines, data processing flows, and agent chains with drag-and-drop interface
- **Real-Time Collaboration** - Built-in support for pair programming, shared sessions, and live code reviews
- **Enterprise Security** - Role-based access control, audit logging, secrets management, and compliance-ready architecture
- **Extensible Plugin System** - Modular plugin architecture for custom integrations, tools, and language support
- **Native Cloud Runtime** - Containerized microservices architecture with Kubernetes orchestration support
- **Multi-Language Support** - First-class support for Python, TypeScript, JavaScript, Go, Rust, and Java
- **Integrated Monitoring** - Distributed tracing, metrics collection, and structured logging via OpenTelemetry
- **Scalable Storage** - Hybrid storage layer with PostgreSQL, Redis, and S3-compatible object stores

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    UI / CLI Layer                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐  │
│  │ Next.js  │  │  Monaco  │  │  Xterm   │  │  React     │  │
│  │ Frontend │  │  Editor  │  │ Terminal │  │  Flow      │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └─────┬──────┘  │
│       │             │             │              │          │
│  ┌────┴─────────────┴─────────────┴──────────────┴──────┐   │
│  │                    CLI (Click)                        │   │
│  └─────────────────────────┬─────────────────────────────┘   │
├────────────────────────────┼─────────────────────────────────┤
│                    ┌───────┴────────┐                        │
│                    │  API Gateway   │                        │
│                    │  (FastAPI +    │                        │
│                    │   HTTP/2 gRPC) │                        │
│                    └───────┬────────┘                        │
├────────────────────────────┼─────────────────────────────────┤
│                    ┌───────┴────────┐                        │
│                    │Workflow Engine │                        │
│                    │(DAG Scheduler  │                        │
│                    │ + Event Bus)   │                        │
│                    └───────┬────────┘                        │
├────────────────────────────┼─────────────────────────────────┤
│                    ┌───────┴────────┐                        │
│                    │Agent Platform  │                        │
│                    │(Orchestrator + │                        │
│                    │ Tool Registry) │                        │
│                    └───────┬────────┘                        │
├────────────────────────────┼─────────────────────────────────┤
│                    ┌───────┴────────┐                        │
│                    │AI Platform     │                        │
│                    │(LLM Gateway +  │                        │
│                    │ Embeddings)    │                        │
│                    └───────┬────────┘                        │
├────────────────────────────┼─────────────────────────────────┤
│                    ┌───────┴────────┐                        │
│                    │ Runtime Engine  │                        │
│                    │(Isolated Exec +│                        │
│                    │ Executor)      │                        │
│                    └───────┬────────┘                        │
├────────────────────────────┼─────────────────────────────────┤
│  ┌──────────┐  ┌──────────┴──────────┐  ┌───────────────┐   │
│  │PostgreSQL│  │       Redis         │  │  S3 / MinIO   │   │
│  │(Storage) │  │   (Cache/Queue)     │  │ (Object Store)│   │
│  └──────────┘  └─────────────────────┘  └───────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Tech Stack

### Backend
- **Framework:** FastAPI (Python 3.11+)
- **ORM:** SQLAlchemy 2.0 + Alembic
- **Validation:** Pydantic v2
- **Runtime:** Uvicorn with ASGI
- **Workers:** Celery + Redis

### Frontend
- **Framework:** Next.js 14 (React 18)
- **State:** Zustand + TanStack Query
- **Styling:** Tailwind CSS + shadcn/ui
- **Editor:** Monaco Editor + Xterm

### Infrastructure
- **Database:** PostgreSQL 16 (asyncpg)
- **Cache:** Redis 7
- **Container Runtime:** Docker + Kubernetes
- **Observability:** OpenTelemetry + Prometheus

### AI/ML
- **LLM Gateway:** OpenAI / Anthropic / Ollama
- **Vector Store:** pgvector
- **Embeddings:** text-embedding-ada-002 / all-MiniLM-L6-v2

## Quick Start

### Option 1: Docker Compose (Recommended)

```bash
git clone https://github.com/lucbruna/SuperDev-AI-Suite.git
cd SuperDev-AI-Suite/SuperDev
docker-compose up -d
```

This starts:
- Backend: http://localhost:8000
- Frontend: http://localhost:3000
- PostgreSQL: localhost:5432
- Redis: localhost:6379
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3001

### Option 2: Local Development

**Backend:**
```bash
cd SuperDev
pip install fastapi uvicorn sqlalchemy pydantic redis httpx psutil
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd SuperDev/frontend
npm install
npm run dev
```

## Project Structure

```
SuperDev/
├── backend/          # REST API, WebSocket, Auth, AI
├── frontend/         # Web Dashboard, IDE, Editor
├── desktop/          # Desktop Application
├── mobile/           # Mobile Clients
├── cli/              # Command Line Interface
├── sdk/              # Official SDKs (Python, TS, Go, Rust)
├── agents/           # AI Agents (Architect, Backend, Frontend...)
├── workflow/         # Workflow Engine & Orchestration
├── runtime/          # Isolated Execution Runtime
├── plugins/          # Plugin Marketplace & Manager
├── ai_router/        # AI Provider Routing & Load Balancing
├── knowledge/        # Knowledge Base & Vector Search
├── database/         # ORM Models & Migrations
├── security/         # Auth, Encryption, Vault
├── observability/    # Logging, Tracing, Metrics
├── monitoring/       # Alerts, Dashboards, Status
├── tests/            # Unit, Integration, E2E Tests
├── docs/             # Documentation
├── examples/         # Example Projects
├── templates/        # Project Templates
├── scripts/          # Build & Deploy Scripts
└── tools/            # Dev Tools & Utilities
```

## API Endpoints

```bash
# Health check
curl http://localhost:8000/health

# List agents
curl http://localhost:8000/api/v1/agents

# Chat with AI
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!"}'
```

## Useful Commands

| Command | Description |
|---------|-------------|
| `docker-compose up -d` | Start all services |
| `docker-compose down` | Stop all services |
| `docker-compose logs -f backend` | View backend logs |
| `make migrate` | Run database migrations |
| `make seed` | Populate database with initial data (admin user, orgs, projects) |
| `make reset-db` | Reset database (drop schema, recreate extensions) |
| `make reset` | Full bootstrap: `reset-db` → `migrate` → `seed` |
| `make win-seed` | Windows PowerShell: populate database |
| `make win-reset` | Windows PowerShell: full bootstrap |
| `python tests/test_all_imports.py` | Test all modules |
| `pytest tests/ -v` | Run all tests |
| `superdev doctor` | Check system status |

### Database Bootstrap

The database is automatically seeded on first backend startup (via the FastAPI lifespan hook). You can also run commands manually:

```bash
# Full bootstrap (drop everything, recreate, seed):
make reset

# Or step by step:
make reset-db    # Drop schema, rebuild extensions
make migrate     # Run Alembic migrations
make seed        # Insert initial data
```

**Seed credentials:**

| Email | Password | Role |
|-------|----------|------|
| `admin@superdev.com` | `admin123` | Super Admin |
| `dev@superdev.com` | `dev123` | Developer |
| `usuario@superdev.com` | `user123` | Standard User |

## Contributing

**We need developers and contributors!** This project is open to the entire GitHub community. We are building and growing together. Whether you are a backend engineer, frontend developer, DevOps specialist, AI/ML researcher, or just getting started — we welcome your contributions!

### How to Contribute

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Areas Where We Need Help

- Backend API development (FastAPI, Python)
- Frontend development (Next.js, React, TypeScript)
- AI/ML model integration and agent development
- DevOps, Docker, and Kubernetes configuration
- Documentation and tutorials
- Testing and quality assurance
- Plugin development
- Mobile app development (React Native / Flutter)
- Bug fixes and feature requests

See [CONTRIBUTING.md](CONTRIBUTING.md) for more details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Community

- **Issues:** [GitHub Issues](https://github.com/lucbruna/SuperDev-AI-Suite/issues)
- **Discussions:** [GitHub Discussions](https://github.com/lucbruna/SuperDev-AI-Suite/discussions)
- **Pull Requests:** [GitHub PRs](https://github.com/lucbruna/SuperDev-AI-Suite/pulls)

---

**Together we build. Together we grow.** Join us in making AI-powered development accessible to everyone.
