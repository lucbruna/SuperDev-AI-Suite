# Visão Geral da Arquitetura

## Projeto do Sistema

SuperDev segue uma arquitetura inspirada em microsserviços com separação clara de responsabilidades.

### Princípios Fundamentais

1. **Modularidade** - Cada módulo é autônomo com seus próprios testes
2. **Extensibilidade** - Sistema de plugins para funcionalidades personalizadas
3. **Segurança** - Execução isolada, RBAC, registro de auditoria
4. **Observabilidade** - Métricas, rastreamento e logs integrados
5. **Escalabilidade** - Escalonamento horizontal via Kubernetes

## Fluxo de Dados

```
Usuário → Frontend → API Gateway → Serviços Backend
                                    ↓
                              AI Router → Provedores (OpenAI, Anthropic, etc.)
                                    ↓
                              Workflow Engine → Runtime Engine → Sandbox
                                    ↓
                              Banco de Dados (PostgreSQL) + Cache (Redis)
```

## Módulos Principais

| Módulo | Descrição | Caminho |
|--------|-----------|---------|
| Backend | API, Auth, Banco, Serviços | `backend/` |
| Frontend | UI Web, Dashboard, IDE | `frontend/` |
| CLI | Interface de linha de comando | `cli/` |
| Agentes | Plataforma de agentes IA | `agents/` |
| Plataforma IA | Roteamento de provedores, streaming | `ai_platform/` |
| Workflow Engine | Workflows baseados em DAG | `workflow_engine/` |
| Runtime Engine | Execução isolada em sandbox | `runtime_engine/` |
| Plataforma Plugins | Marketplace, sandboxing | `plugin_platform/` |
| Enterprise | SSO, faturamento, multi-tenancy | `enterprise/` |

## Pilha Tecnológica

### Backend
- **Framework**: FastAPI (Python 3.12+)
- **Banco de Dados**: PostgreSQL 16 + SQLAlchemy 2.0
- **Cache**: Redis 7
- **Fila**: Redis Streams / Celery
- **Busca**: pgvector para embeddings

### Frontend
- **Framework**: Next.js 14 + React 18
- **Linguagem**: TypeScript 5.3
- **Estilos**: Tailwind CSS 3
- **Estado**: Zustand + React Query
- **Editor**: Monaco Editor

### Infraestrutura
- **Containers**: Docker + Docker Compose
- **Orquestração**: Kubernetes (EKS/AKS/GKE)
- **IaC**: Terraform + Ansible
- **CI/CD**: GitHub Actions
- **Monitoramento**: Prometheus + Grafana

## Arquitetura de Segurança

- Autenticação JWT + API Key
- Controle de Acesso Baseado em Funções (RBAC)
- Controle de Acesso Baseado em Atributos (ABAC)
- Isolamento de plugins (políticas de sistema de arquivos e rede)
- Registro de auditoria para todas as ações
- Gerenciamento de segredos via HashiCorp Vault
