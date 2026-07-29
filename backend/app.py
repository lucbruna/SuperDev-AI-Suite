from __future__ import annotations

import logging

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

logger = logging.getLogger(__name__)


def _safe_include(app: FastAPI, module_path: str, attr: str = "router", prefix: str = "", **kwargs) -> None:
    """Safely import a router and include it in the app, logging if the module is unavailable."""
    try:
        import importlib
        module = importlib.import_module(module_path)
        router = getattr(module, attr)
        if prefix:
            app.include_router(router, prefix=prefix, **kwargs)
        else:
            app.include_router(router, **kwargs)
        logger.debug("Router loaded: %s", module_path)
    except (ImportError, AttributeError) as e:
        logger.warning("Router not available (skipped): %s — %s", module_path, e)


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

    # Core API router
    from backend.api.router import router as api_router
    app.include_router(api_router)

    # Initialize orchestrator and register with system API
    try:
        from backend.api.v1.system import set_orchestrator
        from core.orchestrator import Orchestrator
        orchestrator = Orchestrator()
        set_orchestrator(orchestrator)
        logger.info("Orchestrator initialized")
    except (ImportError, Exception) as e:
        logger.warning("Orchestrator not available: %s", e)

    # Optional routers (gracefully skip if module not yet implemented)
    _safe_include(app, "backend.code_search.api")
    _safe_include(app, "backend.cloud.api", prefix="/api")
    _safe_include(app, "backend.diff.api", prefix="/api")
    _safe_include(app, "backend.collab.api", prefix="/api")
    _safe_include(app, "backend.deploy.engine")
    _safe_include(app, "backend.websocket.handler")
    _safe_include(app, "backend.websocket.studio_handler")
    _safe_include(app, "backend.prompt_hub.api", prefix="/api")
    _safe_include(app, "backend.refactor.engine", prefix="/api")
    _safe_include(app, "backend.api.external")

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