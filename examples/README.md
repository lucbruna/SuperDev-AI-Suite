# SuperDev Examples

Example projects demonstrating SuperDev capabilities.

## Available Examples

| Example | Description | Stack |
|---------|-------------|-------|
| `basic-api/` | REST API with CRUD operations | FastAPI |
| `chatbot/` | AI-powered chatbot | FastAPI + React |
| `fullstack/` | Full-stack web application | Next.js |
| `data-analytics/` | Data & Analytics Engine (Volume 12): coleta métricas de agentes/projetos -> análise -> dashboard + relatório executivo | Python stdlib |
| `testing-quality/` | Testing & Quality Engine (Volume 15): testes -> cobertura -> quality score -> production gate -> deploy real | Python stdlib |
| `security-engine/` | Security Engine (Volume 16): criptografia -> hashing -> vault -> compliance -> threat detection | Python stdlib |
| `devops-quality-gate/` | Quality Gate <-> DevOps: gate bloqueia/aprova deploys reais (rolling/canary/blue-green) | Python stdlib |
| `devops-subsystems/` | DevOps subsistemas integrados: docker build -> CICD -> provision -> deploy com quality gate -> rollback + histórico -> persistência JSON -> destroy (+ teste automatizado pytest) | Python stdlib |

## Running Examples

```bash
cd examples/basic-api
pip install -r requirements.txt
uvicorn main:app --reload
```
