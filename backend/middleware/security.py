"""Security headers middleware — CSP, HSTS, X-Frame-Options, etc."""

from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Adds standard security headers to every HTTP response."""

    def __init__(
        self,
        app,
        csp: str | None = None,
        hsts_max_age: int = 31_536_000,
        frame_options: str = "DENY",
        referrer_policy: str = "strict-origin-when-cross-origin",
    ):
        super().__init__(app)
        self.csp = csp or (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "font-src 'self'; "
            "connect-src 'self'; "
            "frame-ancestors 'none'"
        )
        self.hsts_max_age = hsts_max_age
        self.frame_options = frame_options
        self.referrer_policy = referrer_policy

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        response.headers["Content-Security-Policy"] = self.csp
        response.headers["Strict-Transport-Security"] = f"max-age={self.hsts_max_age}; includeSubDomains"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = self.frame_options
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = self.referrer_policy
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=(), payment=()"
        # Remove server identification
        if "Server" in response.headers:
            del response.headers["Server"]
        return response
