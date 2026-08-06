# Autonomous Developer

Self-directed coding agent for the SuperDev AI Suite. Plans, generates,
modifies, tests, documents and improves code with minimal supervision, using
the Architecture Intelligence graph and the AI Code Knowledge Graph as its
understanding of the codebase.

## Operation flow

```
user request -> Architecture Intelligence -> AI Code Knowledge Graph
        -> Project Planner -> Task Planner -> Code Generator
        -> Refactoring Engine -> Validation Engine -> Test Generator
        -> Code Reviewer -> Documentation Writer -> Git/GitHub -> Deployment
```

Every change runs on a dedicated work branch, is validated and tested, and is
submitted for review. Unrestricted main-branch writes are not allowed.

## Layout

| Directory        | Purpose                                                |
|------------------|--------------------------------------------------------|
| `config/`        | Dataclass configs with `SUPERDEV_AD_*` env overrides   |
| `core/`          | Models, runtime, context, state, orchestration         |
| `planner/`       | Project and task planning                              |
| `generator/`     | Code generation                                        |
| `refactoring/`   | Refactoring engine                                     |
| `bugfix/`        | Bug fixing pipeline                                    |
| `testing/`       | Test generation and execution                          |
| `documentation/` | Documentation writer                                   |
| `review/`        | Code reviewer                                          |
| `reasoning/`     | Planning/reasoning engine                              |
| `agents/`        | Agent definitions                                      |
| `llm/`           | LLM clients and routing                                |
| `prompts/`       | Prompt templates                                       |
| `memory/`        | Working memory / context store                         |
| `integrations/`  | Git, GitHub, MCP, LLM connectors                       |
| `execution/`     | Command execution sandbox                              |
| `validation/`    | Validation engine                                      |
| `monitoring/`    | Metrics, health, anomaly detection                     |
| `reports/`       | Reports                                                |
| `websocket/`     | Realtime task streaming                                |
| `scheduler/`     | Scheduled task runs                                    |
| `frontend/`      | Dashboard views (Next.js app pages)                    |
| `cli/`           | Command-line tools                                     |
| `utils/`         | Shared helpers                                         |
| `docs/`          | Module documentation                                   |
| `tests/`         | Module test suite                                      |

## Runtime data

Task sessions, artifacts and logs land under
`<project>/.superdev/autonomous_developer/` (git-ignored).
