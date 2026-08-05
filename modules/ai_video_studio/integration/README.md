# AI Video Studio — Global Suite Integration (Volume 10)

> **Status:** ✅ 100% — 17 domain connectors + shared integration core + REST API + 21 tests.

O AI Video Studio deixa de ser um módulo isolado: ele publica **17 conectores de
domínio** que integram o studio ao ecossistema SuperDev AI Suite — Enterprise AI,
Agriculture AI, ERP, CRM, HR, Finance, BI, Security, Automation, Notifications,
Knowledge, Cloud, Monitoring, AI Supervisor, API Gateway, Message Bus e Learning.

Cada conector segue o mesmo contrato `DomainConnector` (status / capabilities /
execute) e produz `video_brief` reutilizáveis pelos pipelines do studio.

## Arquitetura

```
modules/ai_video_studio/integration/
├── integration_manager.py   # shared integration core (pre-existente)
├── event_bus.py             # pub/sub (pre-existente)
├── module_registry.py       # registro de módulos (pre-existente)
├── service_locator.py       # localizador de serviços (pre-existente)
├── dependency_manager.py    # gestão de dependências (pre-existente)
├── health_monitor.py        # health checks (pre-existente)
├── integration_cache.py     # cache (pre-existente)
├── integration_statistics.py# estatísticas (pre-existente)
├── integration_logger.py    # logging (pre-existente)
├── connector_base.py        # DomainConnector (contrato + dispatch)
├── _brief.py                # VideoBrief (resultado JSON-serializável)
├── connectors_registry.py   # agrega os 17 conectores (lazy, tolerante)
├── enterprise_ai/           # LLM router, prompts, multi-agent, reasoning,
│                            #   memory, knowledge, embeddings, vector DB
├── agriculture_ai/          # crop/livestock/drone videos, storyboard, clima,
│                            #   colheita, irrigação
├── erp/                     # invoice, sales dashboard, inventory, catalog,
│                            #   treinamento
├── crm/                     # campanhas, ads automáticos, follow-up de leads,
│                            #   onboarding, promoções
├── human_resources/         # onboarding, treinamento, comunicação interna,
│                            #   recrutamento
├── finance/                 # relatórios financeiros, investimentos,
│                            #   accounting dashboard, apresentações
├── business_intelligence/   # dashboards, KPI, relatórios executivos, charts
├── security/                # pontes: permissões, auditoria, criptografia, auth
├── automation/              # workflows, triggers, scheduler, event listener
├── notifications/           # email, whatsapp, telegram, sms, push (outbox local)
├── knowledge/               # busca documental, RAG, busca semântica, memória
├── cloud/                   # aws, azure, google, cloudflare, oracle (dry-run)
├── monitoring/              # métricas, recursos, GPU, render, storage
├── supervisor/              # self-healing, anomalias, previsão, distribuição
├── gateway/                 # REST, WebSocket, gRPC, eventos
├── message_bus/             # kafka, rabbitmq, redis streams, nats, mqtt
└── learning/                # feedback global, RL (bandit), qualidade, prefs
```

### Contrato `DomainConnector` (`connector_base.py`)

Todos os conectores respondem a três métodos públicos:

- `status() -> {domain, description, actions}` — saúde e ações disponíveis;
- `capabilities() -> {domain, description}` — metadados do domínio;
- `execute(action, data) -> dict` — dispatches por tabela, com resultado
  **sempre JSON-serializável**; ação desconhecida → `{ok: False, error: ...}`.

### `VideoBrief` (`_brief.py`)

Geradores de vídeo (agriculture, erp, crm, hr, finance, bi) retornam briefs
estruturados: `{type: "video_brief", domain, title, scenes, narration, voice,
duration_s, meta}` — consumíveis pelo AI Director / AI Storyboard / AI Voice.

### `connectors_registry.py`

Agrega os 17 conectores com **lazy imports** (nunca puxa implementações ao
importar) e **tolerância a falhas**: um conector que não importa vira `None` no
registry sem quebrar os demais (`get_connectors()`, `connector_domains()`,
`connector_count()`).

## Uso (Python)

```python
from modules.ai_video_studio.integration.connectors_registry import get_connectors

connectors = get_connectors()                     # {domain: connector}
connectors["erp"].execute("invoice_video", {"invoice_id": "INV-1", "amount": 1000})
connectors["security"].execute("check_permission", {"role": "viewer", "capability": "export"})
connectors["learning"].execute("submit_quality", {"output_type": "video", "score": 4.5})
```

Via integration manager (já registrados automaticamente):

```python
from modules.ai_video_studio.integration.integration_manager import get_integration_manager

manager = get_integration_manager()
manager.list_connectors()   # 17 conectores registrados
```

## API REST

| Rota | Descrição |
|---|---|
| `GET /api/v1/video-studio/integration/status` | health do integration core |
| `GET /api/v1/video-studio/integration/connectors` | lista os 17 conectores + ações |

## Integração com a plataforma

Este subsistema complementa o **`suite_integration/`** (SuiteBridge): enquanto o
bridge reutiliza a infraestrutura da plataforma (integration engine, JWT, SSRF,
monitoring, workflow), os conectores de domínio expõem **capacidades de negócio**
do studio (gerar vídeo de invoice, storyboard agrícola, avatar para treinamento…)
para os demais módulos do SuperDev AI Suite.

## Testes

`tests/unit/test_connectors_v10.py` — 21 testes cobrindo registro, contrato
(status/capabilities/execute), ações por domínio, endpoints REST e integração com
o integration manager. Rode com:

```bash
python -m pytest tests/unit/test_connectors_v10.py -q --no-cov
```
