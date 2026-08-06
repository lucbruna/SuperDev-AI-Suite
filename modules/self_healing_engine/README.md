# Self-Healing Engine

Detecta, diagnostica, propõe e executa correções controladas no SuperDev AI Suite,
mantendo a plataforma saudável e reduzindo o trabalho manual de manutenção.

## Fluxo

```
Evento do Sistema
        │
        ▼
Health Monitor
        │
        ▼
Diagnostic Engine
        │
        ▼
Root Cause Analyzer
        │
        ▼
Risk Analyzer
        │
        ▼
Repair Planner
        │
        ▼
Validation Engine
        │
        ▼
Approval Policy
        │
        ▼
Repair Executor
        │
        ▼
Test Runner
        │
        ▼
Rollback (se necessário)
        │
        ▼
Documentation → Architecture Graph → Digital Twin
```

## Estrutura

- `config/` — configuração, políticas de segurança/risco, permissões
- `core/` — runtime, kernel, manager, pipeline, contexto, memória, eventos
- `diagnostics/` — checkers de diagnóstico e health score
- `repair/` — planejamento, execução e histórico de correções
- `validation/` — validadores (sintaxe, dependências, arquitetura, segurança)
- `recovery/` — rollback, snapshots, checkpoints, restore, backup
- `prediction/` — predição de falhas, anomalias e riscos
- `prevention/` — guardrails, quality gates e aprovações
- `monitoring/` — monitores de saúde e métricas
- `automation/` — tarefas de manutenção e validação contínua
- `agents/` — agentes especializados e coordenador
- `workflows/` — fluxos de healing, recovery e rollback
- `plugins/` — carregamento e monitoramento de plugins
- `integrations/` — conectores (Architecture Graph, Digital Twin, git, LLMs)
- `memory/` — memória de healing e histórico
- `database/` — repositórios e adaptadores
- `scheduler/` — agendamento de manutenção e validação
- `websocket/` — streams de healing, diagnóstico e alertas
- `frontend/` — dashboard do Self-Healing Engine
- `reports/` — relatórios de healing, incidentes e execução
- `cli/` — interface de linha de comando
- `utils/` — utilitários compartilhados
- `docs/` — documentação
- `tests/` — suítes de teste

## Integração

Trabalha em conjunto com Architecture Graph, Architecture Intelligence,
AI Code Knowledge Graph, Autonomous Developer e Digital Twin, que fornecem
contexto sobre arquitetura, dependências e estado do sistema.

Prioriza segurança e rastreabilidade: correções automáticas respeitam políticas
de validação, possibilidade de rollback e, quando configurado, aprovação humana
antes de alterações de maior impacto.
