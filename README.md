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
| `admin@superdev.com` | `SuperDev@2025` | Super Admin |
| `dev@superdev.com` | `SuperDev@2025` | Developer |
| `usuario@superdev.com` | `SuperDev@2025` | Standard User |

## Mantis Security Review Suite

SuperDev ships with the **Google Mantis security-review skills** installed under `.agents/skills/` — a multi-stage pipeline that audits the codebase for vulnerabilities and produces a structured review packet. The pipeline is orchestrated by `run_mantis.py` (a resumable runner) which delegates the deterministic parts (init, plan crawl, validation, archiving) to the harness `scripts/mantis_pipeline.py`.

### Pipeline stages (16)

The Mantis campaign runs the following stages in order, each producing an artifact that is checked by a deterministic probe before the runner advances (probes marked with * are defined in `run_mantis.py`; the rest rely on downstream artifacts):

| # | Stage | Artifact produced |
|---|-------|-------------------|
| 1 | `history` | `historical_learnings.jsonl` * |
| 2 | `structural-index` | `kb/structural_index/manifest.json` * |
| 3 | `summarize` | `mantis-summary.md` (bounded walk) * |
| 4 | `architecture` | `kb/index.md` + `kb/architecture.md` * |
| 5 | `threat-model` | `kb/THREAT_MODEL.md` * |
| 6 | `plan` | `plan.json` (Mode-A crawl) * |
| 7 | `researcher` | `findings/*.json` * |
| 8 | `dedupe` | deduplicated findings |
| 9 | `review` | review packet markdown |
| 10 | `critic` | critique of the review packet |
| 11 | `reproduce` | `reproducers/` PoCs * |
| 12 | `chain` | chained multi-finding narratives |
| 13 | `patch` | `patch_diff` inside findings JSON * |
| 14 | `calibrate` | `calibration.json` |
| 15 | `reflect` | `learnings.jsonl` (archived per pass) * |
| 16 | `report` | `report/review_packet-latest.md` * |

### Quick start

```bash
# 1) Bootstrap the workspace (creates workspace/ + state file)
python run_mantis.py init

# 2) Run the full pipeline automatically (resumable, skips completed stages)
python run_mantis.py run --auto

# 3) Check progress at any time
python run_mantis.py status

# 4) When all 16 stages are done, archive the pass (increments the pass number)
python run_mantis.py archive
```

### `run_mantis.py` commands

| Command | Description |
|---------|-------------|
| `python run_mantis.py init` | Bootstrap the workspace (delegates to harness) |
| `python run_mantis.py plan` | Mode-A crawl → `plan.json` (delegates to harness) |
| `python run_mantis.py run --auto` | Walk all 16 stages in order; skips completed ones |
| `python run_mantis.py run --interactive` | Pause after each stage and verify its output artifact |
| `python run_mantis.py run --dry-run` | Print the runbook (pending stage prompts) without executing |
| `python run_mantis.py run --stages researcher dedupe` | Run only the given stages |
| `python run_mantis.py run --no-archive` | Skip the automatic archive + pass-increment at the end of a run |
| `python run_mantis.py status` | Show per-stage progress (`x/16 complete`) |
| `python run_mantis.py mark <stage> done` | Manually mark a stage complete |
| `python run_mantis.py reset` | Clear recorded stage statuses |
| `python run_mantis.py validate` | Validate state/plan/findings against `schema.json` |
| `python run_mantis.py archive` | Archive the current pass: findings + KB snapshot + learnings, increment pass |

### How the runner works

- **Resumable checkpoints** live in `workspace/.run_mantis.json`. Re-running `run` continues where you left off — completed stages are detected either by recorded status or by their **output artifact** (deterministic probes).
- **Pending stage prompts** are written to `workspace/runbook/NN_stage.md`; in `--auto` mode the runner prints the prompt for each pending stage and advances once its artifact appears.
- **Pass lifecycle:** when all 16 stages complete, the runner archives the pass (KB snapshot → `workspace/archive/kb/kb_pass_N/`, learnings → `archive/learnings/`, findings moved to trash) and increments the pass counter for the next campaign.
- **Windows-safe:** the runner forces UTF-8 stdout (no cp1252 crashes) and the `summarize` artifact probe uses `os.walk` with excluded dirs (no slow recursive scan over `node_modules`).

### Automatic trigger (post-commit hook)

The suite ships with an **automatic post-commit hook** that runs the fast Mantis check (runbook refresh + validate + status) after **every commit** — no manual step needed when finalizing work.

The hook body is **versioned in the repo** at `.githooks/post-commit` and the installer is `scripts/install_mantis_hooks.sh` (also exposed as `make mantis-hook`). Both ship with the repo, so **every clone gets them** — nothing lives only in your local `.git/`.

#### Enabling the hook in a fresh clone

```bash
# 1) Clone the repo
 git clone <repo-url>
 cd SuperDev

# 2) Enable the hook (one-time, per clone)
 make mantis-hook
#  or: bash scripts/install_mantis_hooks.sh

# 3) Verify the installation state
 bash scripts/install_mantis_hooks.sh --status
```

`--status` reports whether `core.hooksPath` is set, whether the versioned hook is tracked + executable, and whether the runner (`run_mantis.py`) and harness (`scripts/mantis_pipeline.py`) are present — the same checks on every environment (CI, teammates' laptops, containers).

From then on, every `git commit` runs the fast check automatically and prints a summary, e.g.:

```
  [mantis] fast security check after commit (runbook + validate + status)
  [01/16] history         PENDING -> runbook/01_history.md
  ...
  [validate] artifacts valid against schema.json [OK]
  [status] 14 stage(s) pending: history, structural-index, ...
```

#### Windows / Git Bash

The installer is a bash script and needs Git Bash (installed with Git for Windows) or WSL — it will not run in plain `cmd.exe` or PowerShell. From Git Bash:

```bash
bash scripts/install_mantis_hooks.sh
```

The hook itself (`.githooks/post-commit`) is shebang `#!/usr/bin/env bash` and is invoked by git directly, so it also requires a bash-capable environment. The Python runner forces UTF-8 output, so no cp1252 crashes on Windows.

#### Notes

- **Fast by design**: the hook skips the slow Mode-A plan crawl and never archives from a commit hook.
- **Opt out per commit:** `SKIP_MANTIS=1 git commit`.
- **Remove:** `make mantis-hook-remove` (or `bash scripts/install_mantis_hooks.sh --remove`) — unsets `core.hooksPath` and cleans up any legacy `.git/hooks/` copy.
- **Why versioned:** `.git/hooks/` is per-clone and not tracked; putting the hook in `.githooks/` + `core.hooksPath` means the automation ships with the repo and every clone gets it with one command. (The installer even warns if `core.hooksPath` would silently disable other personal hooks you keep in `.git/hooks/`.)
- **Troubleshooting:** if the hook does not fire, run `bash scripts/install_mantis_hooks.sh --status` — it reports each precondition (hooksPath, tracked hook, executable bit, runner, harness). The hook also no-ops safely when `run_mantis.py`/`scripts/mantis_pipeline.py` are absent or Python is missing, so commits are never blocked.
- **Installer exit code:** the installer exits `0` on success, `1` when the runner/harness are missing (fail loudly — the hook itself would still no-op safely). `make mantis-hook` surfaces that as a failure so a non-functional install is never silently accepted.
- **Line endings:** `.gitattributes` forces `eol=lf` on `.githooks/*` and `scripts/*.sh`, so hooks and the installer never break with CRLF `$'\r'` errors on Windows clones.
- Pending stage prompts are written to `workspace/runbook/`; execute them anytime with `python run_mantis.py run --auto`.

### Running the tests

```bash
python -m pytest tests/unit/test_mantis_pipeline.py -v
```

The root `tests/conftest.py` loads `backend.config`, whose env lists (e.g. `CORS_ALLOW_METHODS=GET,POST,...`) are parsed by the `StrList` type in `backend/settings.py` — it accepts both comma-separated values and JSON arrays, so the whole suite runs without `--confcutdir`.

### Artifacts

After a full pass, `workspace/` contains:

```
workspace/
├── plan.json              # Mode-A crawl result (investigations)
├── .run_mantis.json       # Runner checkpoints (stage statuses)
├── findings/              # Researcher output (JSON findings)
├── kb/                    # Knowledge base (architecture, threat model, entities)
├── helpers/               # Patch/analysis helpers
├── reproducers/           # Reproduce-stage PoCs
├── report/                # Final review packets (review_packet-latest.md)
├── runbook/               # Pending stage prompts (NN_stage.md)
├── archive/               # Per-pass KB snapshots (kb_pass_N/) + learnings
├── historical_learnings.jsonl  # History-stage learning archive
└── learnings.jsonl        # Reflect-stage learnings (archived per pass)
```

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
