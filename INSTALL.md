# Installation Guide

## Prerequisites

- **Python** 3.11 or higher
- **Node.js** 20 LTS or higher
- **pnpm** 9 or higher
- **Docker** Desktop 24+ (optional, for containerized setup)
- **PostgreSQL** 16 (optional, Docker provides this)
- **Redis** 7 (optional, Docker provides this)

## Local Development Installation

### 1. Clone the Repository

```bash
git clone https://github.com/superdev/superdev-ai-suite.git
cd superdev-ai-suite
```

### 2. Set Up Python Environment

```bash
python -m venv .venv
# Activate on Linux/macOS:
source .venv/bin/activate
# Activate on Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Activate on Windows (CMD):
.venv\Scripts\activate.bat

pip install -e ".[dev]"
```

### 3. Set Up Frontend

```bash
pnpm install
```

### 4. Configure Environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 5. Start Infrastructure Services

```bash
docker compose up -d postgres redis
```

### 6. Run Database Migrations

> ⚠️ **REQUIRED.** The schema is managed exclusively by Alembic
> (`backend/database/migrations/`). Docker's `init.sql` only bootstraps
> extensions, a legacy 4-table scaffold and the admin seed user — it does
> **not** create the real application schema (agents, workflows, executions,
> providers, ...). The API will fail at runtime if migrations are skipped.

```bash
alembic upgrade head
```

### 7. Start Development Servers

```bash
make dev
```

The API will be available at `http://localhost:8000` and the UI at `http://localhost:3000`.

## Docker Installation

### Using Docker Compose (Recommended)

```bash
# Clone and enter the repository
git clone https://github.com/superdev/superdev-ai-suite.git
cd superdev-ai-suite

# Copy environment configuration
cp .env.example .env

# Build and start all services
docker compose up -d --build

# Run database migrations
docker compose exec api alembic upgrade head
```

Services:
- Frontend: `http://localhost:3000`
- API: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`

### Using Docker Standalone

```bash
# Build the API image
docker build -t superdev-api -f infra/docker/Dockerfile.api .

# Build the frontend image
docker build -t superdev-frontend -f infra/docker/Dockerfile.frontend .

# Run containers
docker run -d --name superdev-postgres -e POSTGRES_DB=superdev -e POSTGRES_USER=superdev -e POSTGRES_PASSWORD=superdev -p 5432:5432 postgres:16
docker run -d --name superdev-redis -p 6379:6379 redis:7
docker run -d --name superdev-api --env-file .env -p 8000:8000 superdev-api
docker run -d --name superdev-frontend --env-file .env -p 3000:3000 superdev-frontend
```

## Production Installation

### Prerequisites

- Kubernetes cluster (or Docker Swarm)
- PostgreSQL 16 with replication
- Redis 7 with sentinel
- S3-compatible object storage
- TLS certificates
- Ingress controller (nginx-ingress, Traefik, etc.)

### Using Kubernetes

```bash
# Apply Kubernetes manifests
kubectl apply -k infra/k8s/overlays/production

# Check deployment status
kubectl get pods -n superdev

# Access the application
kubectl get ingress -n superdev
```

### Configuration

For production, ensure the following environment variables are configured:

```bash
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/superdev
REDIS_URL=redis://:password@host:6379/0
SECRET_KEY=your-256-bit-secret
ENVIRONMENT=production
LOG_LEVEL=INFO
CORS_ORIGINS=https://app.yourdomain.com
```

### Health Checks

- API Health: `GET /api/v1/health`
- Readiness: `GET /api/v1/ready`
- Liveness: `GET /api/v1/live`

## Verification

After installation, verify the setup:

```bash
# Check API status
curl http://localhost:8000/api/v1/health

# Check frontend
curl http://localhost:3000

# Run tests
make test
```

## Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues and solutions.
