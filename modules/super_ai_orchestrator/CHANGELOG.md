# Changelog

All notable changes to the Super AI Orchestrator Core module.

## [1.0.0] - 2026-08-05

### Added
- `config/`: orchestrator, routing, execution and kernel configuration
  dataclasses with deterministic `resolve()`.
- `core/`: Task model, statuses, orchestration context, task requests.
- `events/`: deterministic event bus.
- `kernel/`: priority queue with deterministic work slices per tick,
  cancellation, resumption (checkpoints), rollback and immutable audit trail.
- `scheduler/`: tick-based periodic scheduling.
- `memory/`: namespaced long-term orchestrator memory.
- `governance/`: approval gate + audit trail.
- `monitoring/`, `telemetry/`, `analytics/`: orchestrator health, counters
  and execution analytics.
- `decision/`: Decision Engine (owner, LLM and tool selection by rules).
- `routing/`: capability-based router.
- `planning/`: deterministic step plans.
- `execution/`: task executor with registered handlers (analysis, plan,
  develop, repair, evolve, workflow, agent).
- `llm/`: provider registry (OpenAI, Claude, Gemini, Ollama, DeepSeek,
  Mistral, Llama) with deterministic selection by capability and cost.
- `agents/`: the 12 Chief Agents and their registry.
- `integrations/`: graceful connectors to all sibling modules (Architecture
  Graph, Architecture Intelligence, AI Code Knowledge Graph, Autonomous
  Developer, Digital Twin, Self-Healing Engine, AI Evolution Engine) plus
  toolchain connectors (Git, GitHub, Docker, Kubernetes, MCP, APIs, Database,
  LLMs, Workflow Engine, Multi-Agent, Plugins, Memory Engine, Vector DB,
  Event Bus, Monitoring, Dashboard).
- `api/`: orchestrator facade + FastAPI router mounted at `/api/v1/orchestrator`.
- `cli/`, `reports/`, `frontend/`, `websocket/`: supporting layers.
- `docs/`: architecture and inter-module contracts.
- `tests/`: deterministic unit test suite.
