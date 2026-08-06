# AI Code Knowledge Graph

Central knowledge base for the SuperDev AI Suite. Scans the repository and
builds a semantic graph of files, classes, functions, APIs, databases,
agents, plugins, workflows, prompts, MCP tools, events and their relations.

## Pipeline

```
project -> filesystem scanner -> language parsers -> AST analysis
        -> semantic engine -> knowledge graph builder -> embeddings
        -> vector store -> RAG engine -> agents / dashboards
```

## Layout

| Directory      | Purpose                                                |
|----------------|--------------------------------------------------------|
| `config/`      | Dataclass configs with `SUPERDEV_KG_*` env overrides   |
| `core/`        | Engine, runtime, pipeline, events, state, registry     |
| `scanner/`     | Filesystem + per-language source scanners              |
| `parsers/`     | Language parsers                                       |
| `ast/`         | AST analysis: classes, functions, imports, deps        |
| `graph/`       | Knowledge graph builder, storage, validation           |
| `semantic/`    | Semantic engine, similarity, ontology                  |
| `embeddings/`  | Vector embeddings for modules/classes/functions        |
| `rag/`         | Retrieval-augmented generation over the graph          |
| `llm/`         | Prompt management and LLM routing                      |
| `indexing/`    | Entity indexes (API, DB, workflows, agents, prompts)   |
| `relations/`   | Dependency, call and semantic relation mappers         |
| `analyzer/`    | Architecture, complexity, dead-code, impact analysis   |
| `agents/`      | Knowledge agents (architect, reviewer, search, ...)    |
| `workflows/`   | Workflow engine and mappers                            |
| `plugins/`     | Plugin registry and lifecycle                          |
| `database/`    | SQLite/Postgres/Neo4j/Redis/vector repositories        |
| `cache/`       | Graph, embedding, semantic and query caches            |
| `search/`      | Full-text, semantic, fuzzy and hybrid search           |
| `visualization/`| Graph/timeline/heatmap exporters                      |
| `reports/`     | Architecture and project reports                       |
| `monitoring/`  | Metrics, health, anomaly detection                     |
| `scheduler/`   | Incremental re-indexing, nightly scans                 |
| `websocket/`   | Realtime graph/knowledge streaming                     |
| `integrations/`| Git, GitHub, MCP, LLM connectors                       |
| `cli/`         | Command-line tools                                     |
| `utils/`       | Shared helpers                                         |
| `frontend/`    | Dashboard views (Next.js app pages)                    |

## Runtime data

Scan outputs and snapshots land under `<project>/.superdev/ai_code_knowledge_graph/`
(git-ignored).
