# AI Engine — SuperDev AI Suite v5

Módulo central de inteligência artificial do SuperDev. Responsável por gerenciar provedores de IA, agentes, ferramentas, sessões, conversas e toda a infraestrutura de execução de modelos de linguagem.

## Arquitetura

```
ai/
├── __init__.py          # Inicializador do pacote
├── ai_engine.py         # Engine central: inicializa e coordena toda infraestrutura de IA
├── ai_manager.py        # Gerenciador de sub-módulos (platform, factory, registry, runtime, etc)
├── ai_factory.py        # Factory para criar instâncias de engines, providers, agentes, routers
├── ai_registry.py       # Registro central de agentes, ferramentas e modelos
├── ai_context.py        # Contexto global assíncrono (request_id, session_id, user_id)
├── ai_runtime.py        # Ambiente de execução de tarefas (timeout, concorrência, limites)
├── ai_state.py          # Estado global (agentes, sessões, tarefas, histórico)
├── ai_health.py         # Monitoramento de saúde dos providers e engine
├── ai_metrics.py        # Métricas (contadores, histogramas, export Prometheus)
├── ai_events.py         # Sistema de eventos (emit, on, off, once, async)
├── ai_logger.py         # Logger estruturado com correlação de contexto
├── ai_permissions.py    # Permissões RBAC para operações de IA
├── ai_types.py          # Definições de tipos (TypedDicts, TypeAliases, Literals)
├── ai_protocols.py      # ABCs/Protocols (AIProvider, AIAgent, AITool, AIMemory, AIRouter)
├── ai_interfaces.py     # Interfaces públicas (IAEngineInterface, IAManagerInterface, AIRegistryInterface)
├── ai_models.py         # Modelos de dados Pydantic (AIModel, AgentConfig, Message, Conversation, etc)
├── ai_repository.py     # Camada de persistência (sessions, conversations, agent states, cache)
├── ai_config.py         # Configuração Pydantic BaseSettings (env vars, defaults)
├── ai_constants.py      # Constantes (default models, provider names, cost tables)
├── ai_exceptions.py     # Exceções customizadas (ProviderError, AgentError, etc)
├── ai_utils.py          # Utilitários (token counting, cost estimation, JSON parsing)
└── README.md            # Esta documentação
```

## Quick Start

```python
from ai.ai_engine import AIEngine

async def main():
    async with AIEngine() as engine:
        response = await engine.chat([
            {"role": "user", "content": "Hello!"}
        ])
        print(response["content"])
```

## Dependências

- Python 3.11+
- pydantic >= 2.0
- pydantic-settings >= 2.0

## Módulos Internos

O AI Engine trabalha em conjunto com os seguintes sub-pacotes:

- `ai/core/` — Kernel, Platform, Configuration
- `ai/providers/` — Integrações com OpenAI, Anthropic, Gemini, Ollama, OpenRouter
- `ai/agents/` — Implementações de agentes especializados
- `ai/routing/` — Roteamento inteligente entre providers
- `ai/tools/` — Ferramentas executáveis pelos agentes
- `ai/memory/` — Sistemas de memória (curto e longo prazo)
- `ai/streaming/` — Gerenciamento de streams
- `ai/cache/` — Cache de prompts e respostas
- `ai/registry/` — Registro de agentes e ferramentas
