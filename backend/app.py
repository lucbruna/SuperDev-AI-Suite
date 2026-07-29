from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from backend.config import config
from backend.constants import API_V1_PREFIX, PROJECT_NAME, VERSION
from backend.error_handlers import register_error_handlers
from backend.lifespan import lifespan
from backend.metrics import MetricsMiddleware
from backend.telemetry import configure_metrics, configure_tracing, instrument_fastapi


def create_app() -> FastAPI:
    app = FastAPI(
        title=PROJECT_NAME,
        version=VERSION,
        docs_url=config.app.docs_url,
        openapi_url=config.app.openapi_url,
        root_path=config.app.root_path,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors.allow_origins,
        allow_credentials=config.cors.allow_credentials,
        allow_methods=config.cors.allow_methods,
        allow_headers=config.cors.allow_headers,
        expose_headers=config.cors.expose_headers,
        max_age=config.cors.max_age,
    )

    app.add_middleware(GZipMiddleware, minimum_size=1000)

    allowed_hosts = config.cors.allow_origins
    if allowed_hosts != ["*"]:
        from urllib.parse import urlparse
        allowed_hosts = list({urlparse(o).hostname or o for o in allowed_hosts})
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=allowed_hosts,
    )

    app.add_middleware(MetricsMiddleware)

    register_error_handlers(app)

    configure_tracing()
    configure_metrics()
    instrument_fastapi(app)

    from backend.api.router import router as api_router
    app.include_router(api_router)

    from backend.code_search.api import router as code_search_router
    app.include_router(code_search_router)

    from backend.cloud.api import router as cloud_router
    app.include_router(cloud_router, prefix="/api")

    from backend.diff.api import router as diff_router
    app.include_router(diff_router, prefix="/api")

    from backend.collab.api import router as collab_router
    app.include_router(collab_router, prefix="/api")

    from backend.deploy.engine import router as deploy_router
    app.include_router(deploy_router)

    from backend.websocket.handler import router as ws_router
    app.include_router(ws_router)

    from backend.websocket.studio_handler import router as studio_router
    app.include_router(studio_router)

    from backend.prompt_hub.api import router as prompt_hub_router
    app.include_router(prompt_hub_router, prefix="/api")

    from backend.refactor.engine import router as refactor_router
    app.include_router(refactor_router, prefix="/api")

    from backend.api.external import router as external_router
    app.include_router(external_router)

    from backend.health import HealthChecker, HealthStatus

    @app.get(f"{API_V1_PREFIX}/version")
    async def version_info():
        return {"success": True, "data": {"version": VERSION, "name": PROJECT_NAME}}

    @app.get("/health")
    async def health_check():
        checker = HealthChecker()
        results = await checker.check_all()
        overall = HealthStatus.HEALTHY
        for r in results.values():
            if r.status == HealthStatus.UNHEALTHY:
                overall = HealthStatus.UNHEALTHY
                break
            if r.status == HealthStatus.DEGRADED:
                overall = HealthStatus.DEGRADED
        return {"status": overall, "checks": {k: v.model_dump() for k, v in results.items()}}

    return app


app = create_app()