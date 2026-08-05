# Suite Integration — Volume 10

> **AI Video Studio · Volume 10** — torna o AI Video Studio um **módulo
> nativo do SuperDev AI Suite**: reutiliza a infraestrutura de plataforma
> existente (integração, autenticação, segurança, observabilidade,
> workflows, plugins) em vez de duplicá-la.

O subsistema `suite_integration/` é a ponte entre o studio e a plataforma
SuperDev. Ele **descobre** os componentes de plataforma disponíveis,
**reutiliza** os que existem e **degrada com graça** para equivalentes
locais quando um componente está ausente — o studio nunca quebra e nunca
reimplementa funcionalidade de plataforma.

## Adaptadores

Cada adaptador cobre um serviço de plataforma:

| Adapter | Módulo da plataforma | Ação | Fallback local |
|---|---|---|---|
| `integration` | `SuperDev.integration` | registra o studio no Integration & API Engine (`IntegrationDefinition`) | relata indisponível |
| `auth` | `backend.auth.jwt` | verifica tokens JWT (`verify_token`) | responde `ok:false` |
| `security` | `SuperDev.security.ssrf` | valida URLs contra a política SSRF (CWE-918) | mesma política em stdlib |
| `observability` | `SuperDev.monitoring` | health do MonitoringEngine + métricas | contadores locais |
| `plugins` | `SuperDev.plugin_platform` | registra os 8 plugins oficiais do studio | registry local de descritores |
| `workflow` | `SuperDev.workflow` | registra o pipeline do studio (plan→render→export) como workflow | relata indisponível |

> **Nota:** `SuperDev.plugin_platform` não importa atualmente no repo
> (depende de um pacote `core` de nível superior ausente). O adapter de
> plugins detecta isso e mantém o catálogo de plugins do studio em um
> registry local — a integração fica pronta assim que a plataforma
> importar.

## Uso

```python
import asyncio
from modules.ai_video_studio.suite_integration import get_suite_bridge

bridge = get_suite_bridge()
print(bridge.check())                    # matriz de capacidades da plataforma
print(bridge.manifest())                 # contrato consumir/fornecer do studio
print(bridge.register_with_platform())   # instala no engine de integração + workflows + plugins
print(bridge.validate_url("http://169.254.169.254/x"))   # SSRF: safe False

async def main():
    await bridge.verify_token("...token...")

asyncio.run(main())
```

## API

Todos os endpoints vivem sob `/api/v1/video-studio/suite-integration`:

| Method | Path | Descrição |
|---|---|---|
| `GET` | `/status` | Matriz de capacidades da plataforma (módulos + adapters) |
| `GET` | `/adapters` | Status por adapter (disponibilidade, ações) |
| `GET` | `/manifest` | Contrato do studio com a plataforma (consumes/provides) |
| `POST` | `/register` | Instala o studio no engine de integração, workflows e plugins |
| `POST` | `/verify-token` | Verifica um JWT via o manager da plataforma |
| `POST` | `/validate-url` | Valida uma URL contra a política SSRF |

## Integração com o resto do studio

- O `suite_bridge` também é registrado como serviço no
  `integration/integration_manager` do studio (visível em
  `GET /integration/status`).
- Os testes em `tests/unit/test_suite_integration.py` rodam **contra a
  plataforma real** do repo (SSRF, JWT, integration engine, workflow) e
  cobrem também o fallback local.
