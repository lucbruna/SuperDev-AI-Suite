# Super AI Orchestrator Core — Architecture

Volume 6 of the SuperDev AI Suite advanced modules. The orchestrator is the
"brain of brains": it decides who executes each task (12 Chief Agents), which
LLM serves it (7 providers) and what tools it needs, then drives the task
through a deterministic lifecycle with governance, audit and graceful
integration with every sibling module.

## Design principles

1. **Determinism** — the core has no clock, no network and no LLM calls.
   The same task state always produces the same decision, the same ordering
   and the same outcome. Ordering comes from monotonic sequences, not
   timestamps.
2. **Graceful degradation** — nothing in the orchestrator can break because a
   sibling module or tool is missing. Connectors report structured
   ``unavailable`` / ``delegated`` results instead of raising.
3. **Governance by default** — tasks pass an approval gate. Policies decide
   which kinds always need approval (deploy, recover), which never do
   (monitor, analyze), and which payloads are destructive.
4. **Append-only audit** — every state change is recorded on an immutable
   audit trail and published on an ordered event bus.

## Pipeline

```
task ──▶ decision ──▶ governance gate ──▶ planning ──▶ execution (kernel)
   │        │              │                  │              │
   │   owner / llm /  auto-approve      ordered steps   lifecycle +
   │   requires         or wait              (plan)      audit/events
   │
   └── result ──▶ audit ──▶ reports / dashboard / websocket
```

1. A caller submits a ``TaskRequest`` (API, CLI, scheduler or another module).
2. The **DecisionEngine** selects the owner Chief Agent (capability routing),
   the LLM provider (capability + cost preference) and the required tools.
3. The **GovernanceEngine** applies policy: auto-approve, park for operator
   approval, or reject.
4. The **Planner** produces a deterministic step plan for the task kind.
5. The **kernel** queues by priority (10 = most urgent), schedules slices on
   ``tick``, executes through the **TaskExecutor**, and supports
   cancel / pause / resume / checkpoint / rollback.
6. Every transition is audited and published as an event; the **Monitor**,
   **Analytics**, **reports**, **dashboard payload** and **event hub** consume
   that state.

## Package map

| Package | Responsibility |
|---|---|
| `config/` | `OrchestratorConfig`, `KernelConfig`, `RoutingConfig` (dataclasses + dict overrides) |
| `core/` | `Task`, `TaskRequest`, `TaskStatus`, `OrchestrationContext` |
| `events/` | `Event`, `EventBus` (ordered, in-process, replayable) |
| `kernel/` | `OrchestrationKernel`, `PriorityQueue`, `AuditTrail` |
| `scheduler/` | `PeriodicScheduler` (tick-based, no clock) |
| `memory/` | `MemoryStore` (namespaced, versioned, snapshot/restore) |
| `governance/` | `GovernanceEngine`, `GovernancePolicy` (approval gate) |
| `monitoring/` | `OrchestratorMonitor` (health + metrics) |
| `telemetry/` | `Telemetry` (counters/gauges) |
| `analytics/` | `OrchestratorAnalytics` (rates, distributions, failures) |
| `agents/` | 12 `ChiefAgent`s + `AgentRegistry` |
| `llm/` | `LLMProvider`, `LLMRegistry` (capability + cost selection) |
| `routing/` | `Router` (capability-based kind → agent) |
| `planning/` | `Planner`, `PlanStep` (per-kind templates) |
| `decision/` | `DecisionEngine` (owner / llm / requires) |
| `execution/` | `TaskExecutor` + default kind handlers |
| `integrations/` | `ConnectorRegistry`: 7 sibling + 16 toolchain connectors |
| `api/` | `OrchestratorAPI` facade + FastAPI router (`/api/v1/orchestrator`) |
| `cli/` | stdlib argparse CLI (`python -m modules.super_ai_orchestrator.cli`) |
| `reports/` | `OrchestratorReport` (Markdown) |
| `frontend/` | `DashboardPayload` (JSON-safe dashboard data) |
| `websocket/` | `EventHub` (serializable fan-out wired to the event bus) |
| `docs/` | this file + contracts |

## The kernel

- **Queue**: min-heap ordered by ``(-priority, seq)`` — highest priority, then
  oldest, always wins.
- **Submit**: assigns a monotonic ``seq``, dedupes identical tasks
  (kind + title + payload) while one is active, and either gates or queues.
- **Tick**: processes up to ``slices_per_tick`` slices; pulls the head task,
  marks SCHEDULED, then RUNNING + executes when concurrency allows and an
  executor is registered; otherwise parks it in ``_waiting``.
- **Control**: `approve`, `reject`, `cancel`, `pause` (checkpoint),
  `resume`, `rollback` — all transition-validated.
- **Audit**: every action is recorded (`submit`, `enqueued`, `decided`,
  `gated`, `approved`, `scheduled`, `started`, `completed`, `failed`,
  `cancelled`, `paused`, `resumed`, `rolled_back`, `deduped`).
- **Events**: the same lifecycle is published on the event bus; listeners run
  synchronously in subscription order.

## Integrations

Sibling modules are discovered via ``importlib.util.find_spec`` (no hard
imports) and exposed as connectors:

- `architecture_graph`, `architecture_intelligence`,
  `ai_code_knowledge_graph`, `digital_twin`, `self_healing_engine`,
  `autonomous_developer`, `ai_evolution_engine`

Toolchain connectors (binary-on-PATH or builtin capability):

- `git`, `github`, `docker`, `kubernetes`, `mcp`, `api`, `database`,
  `llm`, `workflow_engine`, `multi_agent`, `plugins`, `memory_engine`,
  `vector_db`, `event_bus`, `monitoring`, `dashboard`

Every `execute()` returns a structured dict and never raises:

| Condition | Result |
|---|---|
| connector unknown | `{"status": "unknown"}` |
| connector unavailable | `{"status": "unavailable"}` |
| available, no handler | `{"status": "delegated"}` |
| handler raises | `{"status": "error", "error": ...}` |
| handler OK | handler's dict (+ `available`, `connector`, `action`) |
