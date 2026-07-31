# LLM Code Navigation Example

Demonstrates the code-navigation pipeline wired into the **`CodeEngine`**:
navigate a real project by dependency and assemble the context that gets
injected into an LLM prompt.

## What it does

1. **Understand** — `CodeEngine.understand(path)` scans the project, builds
   the `SymbolIndex` (classes/functions/imports via AST) and the
   `DependencyGraph` (edges from imports).
2. **Find symbols** — `CodeEngine.find_symbols(path, "order")` searches the
   index via `SymbolIndex.rank(query)` and shows where the matches live —
   already **sorted by relevance** (classes outrank functions, which outrank
   plain imports).
3. **Navigate by dependency** — `CodeEngine.build_llm_context(...)` runs
   **BFS** from the seed file over the dependency graph (dependencies AND
   dependents), bounded by `max_depth`/`max_files`/`max_tokens`.
4. **Rank by relevance** — when a `query` is given, the BFS selection is
   re-ranked by the query symbols found in each file (via `SymbolIndex.rank`,
   weighted by kind: class > function > import). Seed files stay first and
   the most relevant files are injected first into the prompt.
5. **Assemble the prompt** — the ranked files are injected under
   `### FILE: <path>` fences into a ready-to-send prompt.
6. **Survive tight budgets** — `max_file_tokens` caps each injected file:
   oversized files are truncated **in the middle** of their block (head and
   tail kept, marker line in between) so the ranked selection still fits a
   small overall `max_tokens` budget.
6b. **Global budget** — independently of the per-file cap, `max_tokens`
   alone caps the **whole prompt**: trailing files (the least relevant,
   since the selection is ranked) are truncated further in the middle and,
   when even a minimal slice cannot fit, dropped entirely. The result
   reports both `truncated_files` and `dropped_files`.
7. **Ask the LLM with focus** — `CodeEngine.ask_llm(query="Order", ...)`
   sends the anchored prompt to the `LLMEngine` (`ai.llm`) and, using the
   relevance ranking, appends a `Foco: Order, OrderItem, ...` section to the
   instruction so the model is steered toward the key symbols. The result
   includes `focus` with the chosen symbols, the section text, the added
   token overhead and the measured **coverage** (fraction of focus symbols
   mentioned in the reply). Providers are auto-registered from environment
   variables; when none is available a `MockProvider` is registered so the
   example runs without API keys (`mode: mock` in the summary).
8. **Measure the improvement** — a deterministic `FocusEchoProvider`
   (a `MockProvider` that echoes the `Foco:` line) runs the same call with
   and without focus, showing the coverage jump (baseline 0% → 100% with
   focus) and the token overhead.

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

With a tight budget (`max_tokens=600`, `max_file_tokens=30`) the example shows
files being truncated mid-block while the prompt still fits the budget. A
second tight run (`max_tokens=150`, **no** `max_file_tokens`) shows the global
pass alone: trailing files truncated and/or dropped until the assembled prompt
fits. The LLM step sends `query='Order'`, so the prompt carries a `Foco: ...`
section naming the most relevant symbols, and the final step measures the
reply coverage with and without focus.

## Run

```bash
cd SuperDev
python examples/llm-navigation/main.py
```

## Files

| File | Purpose |
|------|---------|
| `main.py` | End-to-end understand → search → BFS → rank → prompt → per-file truncation → global-budget truncation/drops → LLM with focus → improvement measurement |
| `demo_project/` | Tiny multi-package project used as navigation target |
