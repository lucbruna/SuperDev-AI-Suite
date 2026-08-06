# Digital Twin Module

Módulo **Digital Twin** da SuperDev AI Suite: mantém uma representação digital
viva, continuamente sincronizada, da plataforma — estado, relações e evolução
ao longo do tempo.

## Visão geral

O Digital Twin modela os projetos, módulos, serviços, workflows, plugins,
agentes, bancos de dados, APIs e eventos do SuperDev como entidades de um
grafo vivo. A partir dele é possível:

- **Sincronizar** o twin com a realidade (arquivos, banco, integrações);
- **Simular** cenários what-if de mudanças e avaliar impacto/risco;
- **Prever** tendências de métricas e falhas prováveis;
- **Monitorar** a saúde do sistema e emitir alertas;
- **Visualizar e reportar** a topologia e o estado da plataforma.

## Arquitetura

| Pacote | Responsabilidade |
| --- | --- |
| `config/` | Configurações (env `SUPERDEV_DT_*`) e permissões por papel |
| `core/` | Engine, runtime, kernel, pipeline, registro, eventos, estado |
| `api/` | Camada de API determinística (handlers, rotas) |
| `twin_engine/` | Construção, snapshots, validação e serialização do twin |
| `project_model/` | Entidades do modelo de projeto |
| `state_manager/` | Gerenciamento de estados tipados |
| `synchronization/` | Sincronização twin <-> realidade |
| `simulation/` | Simulação de cenários e avaliação de risco |
| `prediction/` | Previsão de tendências e impacto |
| `analytics/` | Análises estatísticas do grafo |
| `metrics/` | Coleta e agregação de métricas |
| `events/` | Barramento de eventos e auditoria |
| `agents/` | Agentes especializados do twin |
| `workflows/` | Orquestração de fluxos |
| `plugins/` | Registro e runtime de plugins |
| `graph/` | Grafo de entidades e consultas |
| `memory/` | Memória persistente do twin |
| `database/` | Runtimes de banco e transações |
| `monitoring/` | Health checks, anomalias e alertas |
| `visualization/` | Exportações visuais (mermaid, graphviz, reactflow) |
| `reports/` | Geração de relatórios (markdown, html) |
| `integrations/` | Conectores (arquitetura, KG, AD, git, MCP, etc.) |
| `websocket/` | Hub de websocket e streams em tempo real |
| `scheduler/` | Agendamento determinístico (tick-based) |
| `frontend/` | Views e dashboard textual |
| `cli/` | Interface de linha de comando |
| `utils/` | Utilidades (texto, arquivos, hashing) |
| `docs/` | Documentação do módulo |
| `tests/` | Helpers de teste |

## Uso

```python
from modules.digital_twin.config import DigitalTwinConfig
from modules.digital_twin.core import DigitalTwinRuntime

config = DigitalTwinConfig.from_env()
config.resolve("C:/projetos/meu_app")

runtime = DigitalTwinRuntime(config=config)
report = runtime.run_cycle()  # sync -> simulate -> predict -> monitor -> report
print(report.summary())
```

## Testes

```bash
python -m pytest tests/unit/test_digital_twin_*.py --no-cov -q
```
