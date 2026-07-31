# LLM Code Navigation Example

Demonstrates the code-navigation pipeline wired into the **`CodeEngine`**:
navigate a real project by dependency and assemble the context that gets
injected into an LLM prompt.

## What it does

1. **Understand** — `CodeEngine.understand(path)` scans the project, builds
   the `SymbolIndex` (classes/functions/imports via AST) and the
   `DependencyGraph` (edges from imports).
2. **Find symbols** — `CodeEngine.find_symbols(path, "order")` searches the
   index for symbols and shows where they live.
3. **Navigate by dependency** — `CodeEngine.build_llm_context(...)` runs
   **BFS** from the seed file over the dependency graph (dependencies AND
   dependents), bounded by `max_depth`/`max_files`/`max_tokens`.
4. **Rank by relevance** — when a `query` is given, the BFS selection is
   re-ranked by the query symbols found in each file (via the `SymbolIndex`,
   weighted by kind: class > function > import). Seed files stay first and
   the most relevant files are injected first into the prompt.
5. **Assemble the prompt** — the ranked files are injected under
   `### FILE: <path>` fences into a ready-to-send prompt.
6. **Ask the LLM** — `CodeEngine.ask_llm(...)` sends the anchored prompt to
   the `LLMEngine` (`ai.llm`) and returns the reply. Providers are
   auto-registered from environment variables; when none is available a
   `MockProvider` is registered so the example runs without API keys
   (`mode: mock` in the summary).

## Demo project

`demo_project/` is a tiny multi-package codebase with real imports —
including **relative** ones, which the resolver handles via the AST `level`:

```
main.py                    -> from services.order_service, from utils.helpers
services/__init__.py      -> from . import helpers
services/order_service.py -> from ..models.order, from ..utils.helpers, from .helpers
services/helpers.py       -> from ..utils.helpers
models/order.py           -> from .base
reporting/sales_report.py -> from ..services.order_service   (dependent!)
```

Seeding the BFS at `main.py` pulls in `order_service.py`, `utils/helpers.py`
and `models/order.py` as dependencies — and `sales_report.py` as a dependent
(reverse edge), which a plain top-down walk would miss. With `query='Order'`
the selection is re-ranked so `models/order.py` (which defines the `Order` and
`OrderItem` classes) is injected into the prompt before less relevant files.

## Run

```bash
cd SuperDev
python examples/llm-navigation/main.py
```

## Files

| File | Purpose |
|------|---------|
| `main.py` | End-to-end understand → search → BFS → rank → prompt → LLM flow |
| `demo_project/` | Tiny multi-package project used as navigation target |
