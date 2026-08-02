# PLANO DE CONSOLIDAÇÃO — Engines Paralelos (P3)

> **Data:** 2026-08-02 · **Domínio:** `workflow`, `knowledge`, `security`, `monitoring`, `api`
> **Base:** AUDIT_REPORT.md (achado C2) · **Método:** inventário com evidência de importadores + fases com gate de verificação

---

## 0. Princípios de governança

1. **Um canônico por domínio** — o grafo de imports deve ter exatamente 1 implementação viva por domínio no serviço (`backend/*`) e 1 na plataforma (raiz), quando o domínio existir nos dois.
2. **O serviço sempre usa `backend/*`** — a camada FastAPI nunca importa engines de plataforma diretamente; se precisar, via adaptador explícito.
3. **Nunca depender de fora para dentro** — pacotes da plataforma (raiz) não podem importar `backend.*` (hoje existe: `monitoring/audit/reporter.py → backend.security.compliance`).
4. **Deprecação antes de remoção** — warnings + docstring + 1 release de compat antes de mover/remover.
5. **Nada de "movimento físico" sem gate verde** — ruff, pytest (181) e suíte de testing/ passando a cada fase.

> Nota estrutural que facilita tudo: `[tool.setuptools.packages.find]` empacota **apenas `backend*`** (`pyproject.toml`). Mover pacotes da raiz para `legacy/` **não altera o wheel** — o risco é apenas de imports internos.

---

## 1. Inventário com evidência (quem usa o quê)

### 1.1 API
| Implementação | Tamanho | Consumidores reais (evidência) |
|---|---|---|
| `backend/api/` | 31 arq. · 6.539 linhas | **Canônico do serviço** — `backend/api/router.py` inclui `v1/` (26 módulos) |
| `api/` (raiz) | 142 arq. · 9.837 linhas | Framework standalone (REST/GraphQL/gRPC/MCP). **Nenhum importador interno encontrado** |

### 1.2 Workflow
| Implementação | Tamanho | Consumidores reais (evidência) |
|---|---|---|
| `backend/workflow/` | 5 arq. · 719 linhas | **Canônico do serviço** — `backend/api/v1/workflow.py`, `backend/workflow_integration/` |
| `core/workflow_engine/` | engine completo | **Canônico da plataforma** — `core/orchestrator/workflow_bridge.py`, `testing/unit`, `testing/integration`, `testing/benchmarks` |
| `workflow_engine/` (raiz) | 18 arq. · 50 linhas | **Shim de compat**: `__init__.py` = `from core.workflow_engine import *` |
| `workflow/` (raiz) | 156 arq. · 4.791 linhas | **Sem importador externo encontrado** (só self-references + `automation/workflow` que tem engine própria) |
| `enterprise_ai_core.workflow_engine` | — | Engine própria dentro do pacote enterprise |
| `automation/workflow/` | — | Engine própria dentro do pacote automation |

### 1.3 Knowledge
| Implementação | Tamanho | Consumidores reais (evidência) |
|---|---|---|
| `backend/knowledge_base/` | 5 arq. · 961 linhas | **Canônico do serviço** — `backend/api/v1/knowledge.py` (models, embeddings, vector store) |
| `backend/knowledge/` | 2 arq. · 160 linhas | `prompt_manager` — pequeno, reexportado; sem conflito |
| `knowledge/` (raiz) | 144 arq. · 8.088 linhas | **Sem importador externo encontrado** |

### 1.4 Security
| Implementação | Tamanho | Consumidores reais (evidência) |
|---|---|---|
| `backend/security/` | 6 arq. · 1.126 linhas | **Canônico do serviço** — RBAC, SSO, compliance, multi-tenancy (`backend/api/v1/admin.py`, `backend/security/router.py`) |
| `security/` (raiz) | 54 arq. · 4.249 linhas | **Canônico de primitivas de plataforma** — `security.ssrf` usado por `ai/tools/http_tool.py`, `data_intelligence/ingestion/api_source.py`, `data/ingestion/api_ingestion.py`; OWASP/SBOM/secrets detector usados por `scanners/`, `test_scanners.py`, `test_sbom.py` |
| ⚠️ Duplicata real | — | `compliance` existe nos DOIS: `security/compliance` e `backend/security/compliance`. `monitoring/audit/reporter.py` já importa `backend.security.compliance` |

### 1.5 Monitoring
| Implementação | Tamanho | Consumidores reais (evidência) |
|---|---|---|
| `backend/monitoring/` | 3 arq. · 169 linhas | **Canônico do serviço** — `AlertManager`, `HealthChecker` (usados pelo app) |
| `monitoring/` (raiz) | 194 arq. · 11.394 linhas | Engine de plataforma (traces, telemetry, alerts). **Importador interno direto não encontrado**; ⚠️ dependência reversa `monitoring/audit/reporter.py → backend.security.compliance` |

---

## 2. Decisão de canônico por domínio

| Domínio | Canônico do serviço | Canônico da plataforma | Ação principal |
|---|---|---|---|
| **API** | `backend/api/` | — (root `api/` é framework) | Arquivar `api/` (raiz) |
| **Workflow** | `backend/workflow/` | `core/workflow_engine/` | Arquivar `workflow/` (raiz) + remover shim `workflow_engine/` após compat; alinhar `automation` e `enterprise_ai_core` ao canônico |
| **Knowledge** | `backend/knowledge_base/` | — | Arquivar `knowledge/` (raiz); absorver `backend/knowledge/` em `knowledge_base` (ou manter como sub-módulo) |
| **Security** | `backend/security/` | `security/` (ssrf/scanners) | **Manter os dois com fronteira documentada**; eliminar duplicata de `compliance` (canônico: `backend.security.compliance`, já usado pelo monitoring root) |
| **Monitoring** | `backend/monitoring/` | `monitoring/` (engine standalone) | Resolver dependência reversa; decidir arquivo do root `monitoring/` após remover acoplamento |

**Classificação final dos pacotes da raiz:**
- 🔴 **Arquivar** (`legacy/`): `api/`, `workflow/`, `knowledge/`
- 🟡 **Shim→remover**: `workflow_engine/` (raiz) — só reexporta `core.workflow_engine`
- 🟢 **Manter**: `security/` (com fronteira), `monitoring/` (condicionado à resolução do acoplamento)

---

## 3. Fases de execução

### Fase 0 — Baseline & governança (½ dia)
- [ ] Rodar baseline: `ruff check backend/` + `pytest` (181) + `testing/` (`python testing/test_all_imports.py`) — registrar saída.
- [ ] Criar `docs/consolidation/DECISIONS.md` com um ADR por domínio (o canônico + o porquê, tabela da seção 2).
- [ ] Criar `scripts/check_engine_imports.py`:
  - Falha se algum pacote marcado 🔴 for importado por código canônico (`backend/`, `core/`, `ai/`, `sdk/`, `cli/`).
  - Falha se `monitoring/` (raiz) importar `backend.*` (regra 3).
  - Rodar no CI (job novo ou passo do `ci.yml`).

### Fase 1 — Deprecação declarada (risco zero) (½–1 dia)
- [ ] `DeprecationWarning` + docstring `"DEPRECATED — use <canonical>"` nos `__init__.py` de: `api/`, `workflow/`, `knowledge/`, `workflow_engine/` (raiz).
- [ ] Confirmar suíte continua 100% verde (warnings não quebram nada).

### Fase 2 — Migração de importadores internos (2–4 dias)
**Workflow**
- [ ] `automation/workflow/` → importar de `core.workflow_engine` (wrapper fino) ou declarar `automation` também deprecated.
- [ ] `enterprise_ai_core/workflow_engine.py` → wrapper sobre `core.workflow_engine` (manter API pública).
- [ ] Confirmar `testing/` (unit/integration/benchmarks) aponta para `core.workflow_engine` (já usa).

**Monitoring (acoplamento reverso)**
- [ ] `monitoring/audit/reporter.py`: já usa `backend.security.compliance` — extrair o `ComplianceEngine` para um pacote neutro **ou** documentar como dependência legítima e mover `monitoring/` inteiro para `legacy/` (ele não tem importador canônico).
- [ ] Decisão registrada no ADR: se nenhum caminho canônico usar `monitoring/`, ele é arquivável inteiro.

**Security (duplicata compliance)**
- [ ] Escolher `backend.security.compliance` como único (já é consumido de fora) — apontar/eliminar `security/compliance` da raiz ou vice-versa conforme o ADR.

### Fase 3 — Movimentação física (`git mv`) (1–2 dias)
- [ ] `git mv api legacy/api` · `git mv workflow legacy/workflow` · `git mv knowledge legacy/knowledge`
- [ ] `git mv workflow_engine legacy/workflow_engine` (shim) — **só após** zero imports de `workflow_engine` fora de `core/`.
- [ ] Rodar `scripts/check_engine_imports.py` — qualquer import quebrado revela consumidor esquecido (esse é o mecanismo de detecção).
- [ ] Adicionar `legacy/` ao `ruff.toml` como ignorado (não roda lint em código morto) e ao `pyproject.toml` (não empacota mesmo — só explicitar).
- [ ] Gate: `ruff` + `pytest` + `testing/` verdes.

### Fase 4 — Remoção (após janela de compat: 1 release)
- [ ] Remover `legacy/` por completo.
- [ ] Entrada no `CHANGELOG.md` documentando a remoção e o canônico final.

---

## 4. Verificação por fase (Definition of Done)

Cada fase só fecha com:
1. `cd backend && ruff check .` → 0 erros;
2. `cd backend && python -m pytest -q` → 181 passed, 0 warnings;
3. `python testing/test_all_imports.py` → OK;
4. `python scripts/check_engine_imports.py` → 0 violações;
5. `cd frontend && npm run typecheck && npx vitest run` → verde (se tocar backend API).

---

## 5. Riscos & mitigações

| Risco | Mitigação |
|---|---|
| Imports dinâmicos (`importlib`/`__import__`) escondidos | Varrer `importlib|__import__` nos domínios antes da Fase 3 |
| Consumidores externos do SDK usando pacotes raiz | Manter shims 1 release (Fase 1 → Fase 4) e documentar no CHANGELOG |
| `enterprise_ai_core`/`automation` dependem de engine própria | Wrapper fino no lugar de reimplementação; testes desses pacotes migram junto |
| Perda de funcionalidade do root `monitoring/` (11K linhas) | Não remover até o ADR mapear funcionalidade ↔ consumidor; se órfão, arquivar com documentação de onde migrar |
| Regressão do `security/` (SSRF usado em runtime por `ai/`) | `security/` NÃO entra no escopo de arquivo — só recebe fronteira documentada |

---

## 6. Métricas de sucesso

- **Pacotes top-level:** de ~100 → alvo ~40 (remoção de `api/`, `workflow/`, `knowledge/`, shim `workflow_engine/` + fusões).
- **1 engine por domínio** no grafo de imports (verificável pelo `check_engine_imports.py`).
- **Zero dependências reversas** (raiz → `backend.*`).
- **Zero `DeprecationWarning`** na suíte ao final.
- **Linhas de código morto removidas:** ~28.7K → alvo < 20K (só com Fase 4).

---

## 7. Prioridade de execução sugerida

1. **Fase 0** (governança + guard) — faz hoje, trava regressões.
2. **Fase 1** (warnings) — faz hoje, risco zero.
3. **Fase 2** (migração) — primeiro **Monitoring acoplamento** (menor), depois **Workflow** (maior ganho).
4. **Fase 3–4** — conforme janela de compat.

**Estimativa:** Fases 0–1 ≈ 1 dia · Fase 2 ≈ 2–4 dias · Fase 3 ≈ 1–2 dias · Fase 4 ≈ 1 dia (pós-release).
