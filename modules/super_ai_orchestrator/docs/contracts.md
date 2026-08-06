# Super AI Orchestrator Core — Contracts

## Facade (`OrchestratorAPI`)

Single entry point used by the router, CLI and frontend. Construct:

```python
from modules.super_ai_orchestrator.api import OrchestratorAPI
api = OrchestratorAPI()  # or OrchestratorAPI(config=..., kernel_config=..., governance_policy=...)
```

| Method | Returns |
|---|---|
| `submit(kind, title, payload=None, priority=None, owner_hint=None, require_approval=None)` | task dict |
| `submit_request(TaskRequest)` | `Task` |
| `tick(slices=None)` | `{"processed": n}` |
| `approve(seq)` / `reject(seq, reason)` | task dict |
| `cancel(seq)` / `pause(seq)` / `resume(seq)` / `rollback(seq)` | task dict |
| `get(seq)` / `tasks(status=None)` | task dict / list |
| `stats()` / `health()` / `metrics()` / `analytics_report()` | dicts |
| `audit()` / `events(event_type=None)` | list of dicts |
| `memory_remember(ns, key, value)` / `memory_recall` / `memory_forget` / `memory_namespaces()` / `memory_keys(ns)` / `memory_snapshot()` | dicts / lists |
| `integrations()` / `invoke(name, action="invoke", **kwargs)` | dicts |
| `governance_policy()` / `config_dict()` / `version()` | dict / str |
| `status()` / `dashboard()` | aggregated dicts (JSON-safe) |

**Errors**: `KeyError` (unknown seq) and `ValueError` (invalid status,
transition, priority) propagate; the router maps them to 404 / 400.

## Task

```
kind: str            # develop, repair, analyze, review, evolve, document,
                     # plan, workflow, monitor, recover, deploy, coordinate, agent
title: str
payload: dict        # arbitrary structured input; owner_hint, llm_prefer,
                     # requires and destructive markers are read here
priority: int        # 1..10 (10 = most urgent)
owner: str | None    # set by the DecisionEngine
llm: str | None      # provider name
requires: tuple      # tool names required
seq: int             # monotonic order assigned by the kernel
status: TaskStatus   # lifecycle (see below)
reason / result / error / attempts / checkpoint / created_at
```

## Lifecycle (`TaskStatus`)

```
PENDING → QUEUED → SCHEDULED → RUNNING → COMPLETED
          ↑           │            ├──▶ FAILED → ROLLED_BACK
   WAITING_APPROVAL ──┘            └──▶ PAUSED → SCHEDULED (resume)
          │
          └──▶ REJECTED
```

Valid transitions (enforced by `Task.transition`):

- `PENDING → QUEUED, CANCELLED`
- `QUEUED → WAITING_APPROVAL, SCHEDULED, CANCELLED`
- `WAITING_APPROVAL → QUEUED, REJECTED, CANCELLED`
- `SCHEDULED → RUNNING, PAUSED, CANCELLED`
- `RUNNING → PAUSED, COMPLETED, FAILED, CANCELLED`
- `PAUSED → SCHEDULED, CANCELLED, ROLLED_BACK`
- `FAILED → ROLLED_BACK`

Terminal: `COMPLETED`, `FAILED`, `CANCELLED`, `ROLLED_BACK`, `REJECTED`.

## Events

Published on the event bus (deterministic `seq`, replayable `log`):

`orchestrator.started/stopped`, `task.submitted/decided/queued/waiting_approval/
approved/rejected/scheduled/started/checkpointed/paused/resumed/completed/
failed/cancelled/rolled_back`, `decision.made`, `kernel.queue_full`,
`kernel.deduped`.

`EventBus.subscribe(listener)` returns an unsubscribe callable; `history(type)`
replays recorded events in order.

## Configuration

`OrchestratorConfig`: `default_priority=5`, `audit_enabled`, `checkpoint_enabled`,
`resume_capacity=16`, `max_attempts=1`, `log_level`.

`KernelConfig`: `slices_per_tick=3`, `queue_capacity=256`, `dedupe_enabled=True`,
`min_priority=1`, `max_priority=10`, `max_concurrent=4`,
`governance_required=True`, `rollback_on_failure=False`.

`GovernancePolicy`: `approval_kinds={deploy, recover}`,
`auto_approve_kinds={monitor, analyze}`, `max_priority_without_approval=8`,
`destructive_markers={delete, drop, force}`. Approval decision order:
auto-approve kinds → approval kinds → priority threshold → destructive
markers → kernel-wide `governance_required`.

## Decision rules

- **Owner**: capability routing — the Router maps each kind to the capable
  agent with the best match; an `owner_hint` is honoured only when the hinted
  agent can handle the kind.
- **LLM**: providers (`claude 0.95/0.015`, `openai 0.90/0.020`,
  `gemini 0.85/0.010`, `deepseek 0.80/0.001`, `mistral 0.75/0.002`,
  `ollama 0.70/0.0`, `llama 0.65/0.0`) are selected by required capabilities
  (CODING, REASONING, ANALYSIS, PLANNING, OPERATIONS, VISION, FAST, CHEAP,
  LOCAL); default = highest quality, `llm_prefer="cheap"` = lowest cost,
  `llm_prefer="local"` = best LOCAL.
- **Requires**: per-kind defaults plus payload `requires` and capability keys
  (`git`, `rag`, `memory`, `docker`, `mcp`, `db`, `api`).

## Router (`/api/v1/orchestrator`)

Mounted via `_safe_include` in `backend/app.py`. Envelope
`{"success": bool, "data": ...}`; `ValueError` → 400, `KeyError` → 404.

`GET /status /config /governance /health /metrics /analytics /audit /events
/memory /integrations /dashboard`, `POST /tasks`, `GET/POST /tasks/{seq}`,
`POST /tasks/{seq}/approve|reject|cancel|pause|resume|rollback`,
`POST /tick`, `POST /memory`, `GET/DELETE /memory/{namespace}/{key}`,
`POST /integrations/{name}/invoke`.

## CLI

`python -m modules.super_ai_orchestrator.cli <command>` (stdlib argparse).
Commands: `status health metrics analytics audit governance config dashboard
integrations submit tick approve reject cancel pause resume rollback task
tasks events invoke memory-set memory-get memory-del memory-keys
memory-namespaces`. JSON output, exit 0 on success / 1 on error.
