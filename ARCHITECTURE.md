# Architecture

SuperDev AI Suite follows a layered architecture with clear separation of concerns. Each layer is independently deployable and communicates via well-defined interfaces.

## Layer Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                        PRESENTATION LAYER                         │
│  ┌─────────────────┐  ┌──────────────────┐  ┌────────────────┐  │
│  │  Web UI          │  │  CLI Interface   │  │  REST / gRPC   │  │
│  │  (Next.js 14)    │  │  (Click + Rich)  │  │  (API Clients)  │  │
│  └────────┬────────┘  └────────┬─────────┘  └───────┬────────┘  │
└───────────┼─────────────────────┼─────────────────────┼──────────┘
            │                     │                     │
┌───────────┼─────────────────────┼─────────────────────┼──────────┐
│           │        API GATEWAY LAYER                  │          │
│  ┌───────┴─────────────────────┴─────────────────────┴───────┐  │
│  │                    FastAPI Application                       │  │
│  │  ┌─────────┐ ┌──────────┐ ┌──────────┐ ┌───────────────┐  │  │
│  │  │ Auth    │ │ Rate     │ │ Request  │ │ WebSocket     │  │  │
│  │  │ Middleware│ │ Limiter  │ │ Validator│ │ Manager       │  │  │
│  │  └─────────┘ └──────────┘ └──────────┘ └───────────────┘  │  │
│  └─────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                      WORKFLOW ENGINE LAYER                        │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌─────────┐ │ │
│  │  │ DAG        │ │ Step       │ │ Event Bus  │ │ State   │ │ │
│  │  │ Scheduler  │ │ Executor   │ │ (Redis Pub)│ │ Manager │ │ │
│  │  └────────────┘ └────────────┘ └────────────┘ └─────────┘ │ │
│  └─────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                       AGENT PLATFORM LAYER                        │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌────────────┐ │ │
│  │  │ Agent     │ │ Tool      │ │ Memory    │ │ Planner   │ │ │
│  │  │ Registry  │ │ Registry  │ │ Store     │ │ Executor  │ │ │
│  │  └───────────┘ └───────────┘ └───────────┘ └────────────┘ │ │
│  └─────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                         AI PLATFORM LAYER                         │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────────┐ │ │
│  │  │ LLM      │ │ Prompt   │ │ Embedding│ │ Vector Store  │ │ │
│  │  │ Gateway  │ │ Manager  │ │ Service  │ │ (pgvector)    │ │ │
│  │  └──────────┘ └──────────┘ └──────────┘ └───────────────┘ │ │
│  └─────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                       RUNTIME ENGINE LAYER                        │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────────┐ │ │
│  │  │ Sandbox  │ │ Code     │ │ Resource │ │ Network       │ │ │
│  │  │ Manager  │ │ Runner   │ │ Monitor  │ │ Policy        │ │ │
│  │  └──────────┘ └──────────┘ └──────────┘ └───────────────┘ │ │
│  └─────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                      STORAGE / DATA LAYER                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │  PostgreSQL   │  │    Redis     │  │  S3 / MinIO         │   │
│  │  - Main DB    │  │  - Cache     │  │  - File Storage     │   │
│  │  - pgvector   │  │  - Queue     │  │  - Artifacts        │   │
│  │  - Migrations │  │  - Sessions  │  │  - Backups          │   │
│  └──────────────┘  └──────────────┘  └──────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
```

## Layer Descriptions

### 1. Presentation Layer (UI/CLI)

The top-most layer provides multiple interfaces for users to interact with the platform:

- **Web UI:** Built with Next.js 14 and React 18, featuring Monaco Editor for code editing, Xterm.js for terminal emulation, React Flow for workflow visualization, and Recharts for data visualization.
- **CLI:** A command-line interface built with Click and Rich for terminal-based interaction, scripting, and automation.
- **API Clients:** REST and gRPC clients for programmatic access from external tools and CI/CD systems.

### 2. API Gateway Layer

The gateway is implemented as a FastAPI application that serves as the single entry point for all client requests:

- **Authentication Middleware:** JWT-based authentication with support for OAuth2, SAML, and API keys
- **Rate Limiter:** Token bucket algorithm with per-user and per-endpoint limits
- **Request Validator:** Pydantic-based request validation with automatic error responses
- **WebSocket Manager:** Manages WebSocket connections for real-time features

### 3. Workflow Engine Layer

Orchestrates complex multi-step processes defined as directed acyclic graphs (DAGs):

- **DAG Scheduler:** Topological sort and scheduling of workflow steps
- **Step Executor:** Executes individual workflow steps with retry logic
- **Event Bus:** Redis Pub/Sub for inter-step communication
- **State Manager:** Tracks workflow execution state and history

### 4. Agent Platform Layer

Provides the framework for building and running AI agents:

- **Agent Registry:** Catalog of available agent types and configurations
- **Tool Registry:** Collection of tools that agents can use (code execution, web search, file operations)
- **Memory Store:** Short-term and long-term memory for agents
- **Planner-Executor:** Decomposes complex tasks into executable sub-tasks

### 5. AI Platform Layer

The AI/ML layer provides access to language models and embedding services:

- **LLM Gateway:** Unified interface for multiple LLM providers (OpenAI, Anthropic, Ollama)
- **Prompt Manager:** Template-based prompt management with version control
- **Embedding Service:** Generates vector embeddings for semantic search
- **Vector Store:** pgvector-based similarity search

### 6. Runtime Engine Layer

Provides sandboxed execution environments for running untrusted code:

- **Sandbox Manager:** Creates and manages isolated execution environments
- **Code Runner:** Executes code in multiple languages with timeout enforcement
- **Resource Monitor:** Tracks CPU, memory, and disk usage per execution
- **Network Policy:** Controls network access from within sandboxes

### 7. Storage Layer

Persistent storage and caching infrastructure:

- **PostgreSQL:** Primary database with pgvector extension for vector search
- **Redis:** Caching, session management, and message queuing
- **S3/MinIO:** Object storage for files, artifacts, and backups

## Data Flow

```
User Request
    │
    ▼
┌─────────────┐
│  API Gateway │──► Auth Check ──► Rate Limit ──► Validation
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Workflow   │──► DAG Resolution ──► Step Scheduling
│  Engine     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Agent      │──► Agent Selection ──► Tool Resolution
│  Platform   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  AI         │──► LLM Call ──► Embedding Search
│  Platform   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Runtime    │──► Code Execution ──► Result Collection
│  Engine     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Storage    │──► Persist Results
└─────────────┘
```

## Communication Patterns

- **Synchronous:** REST/gRPC for request-response operations
- **Asynchronous:** Redis Pub/Sub and Celery for background tasks
- **Real-time:** WebSockets for streaming, collaboration, and live updates
- **Event-driven:** Event bus for decoupled inter-service communication

## Scalability

Each layer can be scaled independently:

- **API Gateway:** Horizontal scaling with load balancer
- **Workflow Engine:** Partitioned by workflow ID
- **Agent Platform:** Pooled agent workers
- **AI Platform:** Connection pooling and request batching
- **Runtime Engine:** Per-sandbox resource limits
- **Storage:** Read replicas, connection pooling, and caching
