# Quick Start

Get SuperDev AI Suite running in under 5 minutes.

## Prerequisites

- Docker Desktop 24+

## Quick Start with Docker

```bash
# Clone the repository
git clone https://github.com/superdev/superdev-ai-suite.git
cd superdev-ai-suite

# Copy environment configuration
cp .env.example .env
# ⚠️ SECRET_KEY, JWT_SECRET_KEY, POSTGRES_PASSWORD and GRAFANA_ADMIN_PASSWORD
# are required — generate them with `openssl rand -hex 32` (or -hex 16 for the
# passwords) and fill them into .env before starting.

# Start all services
docker compose up -d --build

# ⚠️ Run database migrations — REQUIRED.
# The Docker init.sql only bootstraps extensions, the legacy 4-table scaffold
# and the admin seed user. The real schema (agents, workflows, executions,
# providers, ...) is managed exclusively by Alembic. Skipping this step leaves
# the API with a broken schema.
docker compose exec api alembic upgrade head

# Done! Open in browser
open http://localhost:3000
```

## Quick Start with Local Setup

```bash
# Clone and enter directory
git clone https://github.com/superdev/superdev-ai-suite.git
cd superdev-ai-suite

# Set up Python
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\Activate.ps1
pip install -e ".[dev]"

# Set up frontend
pnpm install

# Configure environment
cp .env.example .env
# ⚠️ SECRET_KEY, JWT_SECRET_KEY, POSTGRES_PASSWORD and GRAFANA_ADMIN_PASSWORD
# are required — generate them with `openssl rand -hex 32` (or -hex 16 for the
# passwords) and fill them into .env before starting.

# Start Postgres + Redis (if not already running)
docker compose up -d postgres redis

# ⚠️ Run database migrations — REQUIRED (see note above).
alembic upgrade head

# Start dev servers
make dev
```

## What's Next?

- **Explore the API:** Visit `http://localhost:8000/docs` for Swagger documentation
- **Create a workflow:** Navigate to Workflows in the UI and create your first DAG
- **Run an agent:** Go to Agents and launch a code review agent
- **Generate code:** Use the AI assistant panel to generate boilerplate code

## Key Commands

```bash
make dev          # Start all development servers
make test         # Run the test suite
make lint         # Lint all code
make typecheck    # Run type checking
make build        # Build for production
make docker-build # Build Docker images
make clean        # Clean build artifacts
```

## Default Credentials

All seed users share the same password `SuperDev@2025`:

| Email | Role |
|-------|------|
| `admin@superdev.com` | Super Admin |
| `dev@superdev.com` | Developer |
| `usuario@superdev.com` | Standard User |

> ⚠️ **Change all passwords in production!**

- **API:** JWT tokens issued at `POST /api/v1/auth/login`

## API Endpoints

| Endpoint               | Description             |
|------------------------|-------------------------|
| `GET /api/v1/health`   | Health check            |
| `POST /api/v1/auth/login` | User login          |
| `GET /api/v1/workflows` | List workflows         |
| `POST /api/v1/agents/run` | Run an agent        |
| `GET /api/v1/projects` | List projects          |
