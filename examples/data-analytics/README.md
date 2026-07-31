# Data & Analytics Engine Example (Volume 12)

Integrates the SuperDev **Data & Analytics Engine** with real suite components:
agent activity (`AgentManager`) and project snapshots (`ProjectEngine`).

## What it does

1. **Collects** agent activity (duration, tokens, cost) and project metrics
   (tasks, errors, cost) from the live suite.
2. **Ingests & processes** the records through the DataEngine.
3. **Analyzes** costs and trends (descriptive + pattern detection).
4. **Builds BI KPIs** (e.g. total agent cost) and an executive dashboard spec.
5. **Forecasts** task completion for the next 5 periods.
6. **Renders an executive report** and persists outputs to `output/`.

If the suite's `ai`/`project` modules are not importable, the example falls
back to demo data so it can run standalone.

## Run

```bash
cd SuperDev
python examples/data-analytics/main.py
```

## Outputs

- `examples/data-analytics/output/executive_report.md` — executive report
- `examples/data-analytics/output/metrics.json` — engine metrics snapshot

## Files

| File | Purpose |
|------|---------|
| `main.py` | End-to-end collection → analysis → report flow |
| `output/` | Generated artifacts (created on run) |
