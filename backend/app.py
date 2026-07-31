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

    # Security: reject wildcard origins combined with credentials
    cors_origins = config.cors.allow_origins
    if "*" in cors_origins and config.cors.allow_credentials:
        logger.warning(
            "CORS: wildcard origin with credentials is insecure. "
            "Setting allow_credentials=False."
        )
        config.cors.allow_credentials = False

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
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
    # Add common test hosts for dev/test environments
    if config.app.environment != "production":
        allowed_hosts.extend(["testserver", "test", "localhost", "127.0.0.1"])
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=allowed_hosts,
    )

    # Authentication middleware
    try:
        from backend.middleware.authentication import AuthMiddleware
        app.add_middleware(AuthMiddleware)
    except ImportError:
        logger.warning("Auth middleware not available")

    # Security headers
    try:
        from backend.middleware.security import SecurityHeadersMiddleware
        app.add_middleware(SecurityHeadersMiddleware)
    except ImportError:
        logger.warning("Security headers middleware not available")

    # Request size limiting (10MB max)
    try:
        from backend.middleware.request_size_limit import RequestSizeLimitMiddleware
        app.add_middleware(RequestSizeLimitMiddleware, max_body_size=10 * 1024 * 1024)
    except ImportError:
        logger.warning("Request size limit middleware not available")

    app.add_middleware(MetricsMiddleware)

    # Rate limiting middleware
    try:
        from backend.middleware.rate_limit import RateLimitMiddleware
        app.add_middleware(RateLimitMiddleware, max_requests=100, window_seconds=60)
    except ImportError:
        logger.warning("Rate limit middleware not available")

    # Endpoint-specific rate limiting
    try:
        from backend.middleware.endpoint_rate_limit import EndpointRateLimitMiddleware
        app.add_middleware(
            EndpointRateLimitMiddleware,
            endpoint_limits={
                "/api/v1/auth/*": 20,
                "/api/v1/ai/*": 10,
                "default": 100,
            },
            window_seconds=60,
        )
    except ImportError:
        logger.warning("Endpoint rate limit middleware not available")

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
    _safe_include(app, "backend.ai_api")

    # Ecosystem modules
    _safe_include(app, "backend.notifications.router", prefix="/api/v1/notifications", tags=["notifications"])
    _safe_include(app, "backend.notifications.email_router", prefix="/api/v1/email", tags=["email"])
    _safe_include(app, "backend.security.router", prefix="/api/v1/sso", tags=["sso"])
    _safe_include(app, "backend.backup.router", prefix="/api/v1/backup", tags=["backup"])
    _safe_include(app, "backend.export_import.router", prefix="/api/v1/data", tags=["export-import"])
    _safe_include(app, "backend.i18n.router", prefix="/api/v1/i18n", tags=["i18n"])
    _safe_include(app, "backend.search.router", prefix="/api/v1/search", tags=["search"])

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
