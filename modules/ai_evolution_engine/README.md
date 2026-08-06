# AI Evolution Engine

Volume 5 of the SuperDev AI Suite advanced modules. Continuously analyses the
platform and proposes its evolution: architecture quality, technical debt,
performance, dependencies, roadmap and innovation — without modifying anything
automatically.

## Principles

- **Deterministic**: same input state produces the same analysis. No clock,
  network or LLM calls inside the core.
- **Non-invasive**: the engine observes and recommends; it never mutates the
  project by itself. Changes are executed by other modules (Autonomous
  Developer, Self-Healing Engine) after approval.
- **Integration-first**: connectors to the sibling modules (Architecture
  Graph, Architecture Intelligence, AI Code Knowledge Graph, Digital Twin,
  Self-Healing Engine, Autonomous Developer) degrade gracefully when a module
  is not installed.
- **Governed**: every recommendation flows through the approval workflow
  before it becomes roadmap work.

## Pipeline

```
platform state ─▶ analytics ─▶ evolution analysis ─▶ learning
    ─▶ recommendations ─▶ forecasting ─▶ governance approval
    ─▶ roadmap ─▶ reports
```

## Layout

| Path | Purpose |
| --- | --- |
| `config/` | Deterministic configuration dataclasses |
| `core/` | Engine, kernel, manager, pipeline, context, events, state, memory |
| `evolution/` | Continuous + domain-specific evolution analysis |
| `analytics/` | Platform analytics (architecture, dependency, debt, quality, trend) |
| `recommendation/` | Recommendation engine and generators |
| `forecasting/` | Growth, debt, capacity forecasts |
| `optimization/` | Optimization suggestions |
| `learning/` | Pattern, incident and feedback learning |
| `governance/` | Policies, approval workflow, audit, decision registry |
| `roadmap/` | Roadmap engine, priorities, milestones, releases |
| `benchmarking/` | Internal + performance benchmarks |
| `innovation/` | Technology tracking and modernization ideas |
| `agents/` | Per-domain agent definitions |
| `workflows/` | Orchestrated evolution workflows |
| `plugins/` | Plugin registry and evaluation |
| `integrations/` | Connectors to sibling modules and external tools |
| `monitoring/` | Evolution monitor, alerts, metrics |
| `memory/` | Long-term evolution memory |
| `database/` | Repository adapters |
| `websocket/` | Real-time streams |
| `scheduler/` | Periodic analysis scheduling |
| `api/` | REST surface |
| `cli/` | Command line entry points |
| `utils/` | Shared helpers |
| `tests/` | Unit test suite |

## Quick start

```python
from modules.ai_evolution_engine.core import EvolutionManager
from modules.ai_evolution_engine.recommendation import Recommendation

manager = EvolutionManager()
manager.start()

result = manager.analyze()          # -> EngineResult (analysis report)
rec = Recommendation(kind="performance", title="warm the cache",
                     impact_score=0.8, effort_score=0.3, risk_score=0.2)
manager.recommend(rec)              # register as draft
manager.submit_for_approval(rec)    # governance gate
manager.approve(rec)                # operator approval
plan = manager.plan_roadmap([rec])  # -> {"planned": 1, "items": [...]}
```

## Integration

The `integrations/` package exposes `IntegrationRegistry` which lazily imports
sibling modules and reports availability. Each connector never raises when the
target module is missing; it reports `available=False` instead.

```python
from modules.ai_evolution_engine.integrations import build_default_registry

registry = build_default_registry()
registry.summary()        # -> {"self_healing": True, "knowledge_graph": False, ...}
registry.collect_all(ctx) # -> per-connector payloads, never raises
```
