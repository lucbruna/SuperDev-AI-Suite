# Super AI Orchestrator Core

Volume 6 of the SuperDev AI Suite advanced modules. The "brain of brains":
a central coordinator that decides **who** executes each task, **which LLM**
serves it, and **what tools** it needs (RAG, memory, git, docker, MCP), then
orchestrates execution across every sibling module.

Without it, the modules work in isolation. With it, they collaborate.

## What it decides

- **Who runs this task?** Planner, Developer, Repair, Evolution, Workflow,
  another agent — the Decision Engine chooses.
- **Which LLM?** OpenAI, Claude, Gemini, Ollama, DeepSeek, Mistral, Llama.
- **What does it need?** RAG, memory, git, docker, MCP, database, APIs.

## Kernel capabilities

- Priority queues and deterministic scheduling (work slices per tick).
- Cancellation, resumption (checkpoints), rollback and full audit trail.

## Principles

- **Deterministic**: the same task state always produces the same decision.
  No clock, network or LLM calls inside the core.
- **Non-invasive**: the orchestrator decides and delegates; it never mutates
  the project by itself. Execution is delegated to sibling modules after
  governance approval.
- **Integration-first**: connectors to every sibling module (Architecture
  Graph, Architecture Intelligence, AI Code Knowledge Graph, Autonomous
  Developer, Digital Twin, Self-Healing Engine, AI Evolution Engine, plus
  toolchain: git/github/docker/kubernetes/mcp/apis/db/llm) degrade gracefully
  when a module is not installed.
- **Governed**: tasks and their decisions flow through the approval flow.

## Layout

| Path | Purpose |
| --- | --- |
| `config/` | Deterministic configuration dataclasses |
| `core/` | Task model, statuses, orchestration context |
| `events/` | Deterministic event bus |
| `kernel/` | Priority queue, slices, cancel/resume/checkpoint/rollback/audit |
| `scheduler/` | Tick-based periodic scheduling |
| `memory/` | Long-term orchestrator memory |
| `governance/` | Approval gate and audit |
| `monitoring/` | Orchestrator health and metrics |
| `telemetry/` | Deterministic counters |
| `analytics/` | Execution analytics |
| `decision/` | Who runs it, which LLM, which tools |
| `routing/` | Capability-based task routing |
| `planning/` | Deterministic step plans |
| `execution/` | Task executor with registered handlers |
| `llm/` | Provider registry (metadados determinísticos) |
| `agents/` | The 12 Chief Agents and their registry |
| `integrations/` | Connectors to all sibling modules + toolchain |
| `api/` | Orchestrator facade + FastAPI router |
| `cli/` | Command line entry points |
| `reports/` | Markdown report generator |
| `frontend/` | Dashboard payload builder |
| `websocket/` | Real-time event hub |
| `docs/` | Architecture and contracts |
| `tests/` | Deterministic unit test suite |

## Quick start

```python
from modules.super_ai_orchestrator.core import Task
from modules.super_ai_orchestrator.kernel import OrchestrationKernel
from modules.super_ai_orchestrator.decision import DecisionEngine

kernel = OrchestrationKernel()
decision = DecisionEngine()

task = Task(kind="evolve", title="reduce coupling in billing")
decision.decide(task)          # sets owner, llm, requires
kernel.submit(task)
kernel.tick(3)                 # process work slices
kernel.audit()                 # full audit trail
```

## Status

Implemented and tested: config, core, events, kernel, scheduler, memory,
governance, monitoring, telemetry, analytics, decision, routing, planning,
execution, llm registry, agents (12 Chief Agents), integrations (graceful
connectors), api facade + FastAPI router, cli, reports, frontend payload,
websocket hub, docs, deterministic test suite.
