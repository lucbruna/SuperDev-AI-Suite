"""Unit tests for security middleware, request ID middleware."""

import uuid

import pytest
from starlette.testclient import TestClient
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import JSONResponse


async def _dummy_endpoint(request):
    return JSONResponse({"ok": True})


class TestSecurityHeadersMiddleware:
    def _get_app(self):
        from backend.middleware.security import SecurityHeadersMiddleware

        app = Starlette(routes=[Route("/test", _dummy_endpoint)])
        app.add_middleware(SecurityHeadersMiddleware)
        return app

    def test_adds_x_content_type_options(self):
        client = TestClient(self._get_app())
        resp = client.get("/test")
        assert resp.headers.get("X-Content-Type-Options") == "nosniff"

    def test_adds_x_frame_options(self):
        client = TestClient(self._get_app())
        resp = client.get("/test")
        assert resp.headers.get("X-Frame-Options") == "DENY"

    def test_adds_hsts(self):
        client = TestClient(self._get_app())
        resp = client.get("/test")
        assert "max-age=31536000" in resp.headers.get("Strict-Transport-Security", "")

    def test_adds_csp(self):
        client = TestClient(self._get_app())
        resp = client.get("/test")
        assert "Content-Security-Policy" in resp.headers

    def test_custom_csp(self):
        from backend.middleware.security import SecurityHeadersMiddleware

        app = Starlette(routes=[Route("/test", _dummy_endpoint)])
        app.add_middleware(SecurityHeadersMiddleware, csp="default-src 'none'")
        client = TestClient(app)
        resp = client.get("/test")
        assert resp.headers["Content-Security-Policy"] == "default-src 'none'"

    def test_adds_referrer_policy(self):
        client = TestClient(self._get_app())
        resp = client.get("/test")
        assert resp.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"

    def test_adds_permissions_policy(self):
        client = TestClient(self._get_app())
        resp = client.get("/test")
        assert "camera=()" in resp.headers.get("Permissions-Policy", "")


class TestRequestIDMiddleware:
    def _get_app(self):
        from backend.middleware.request_id import RequestIDMiddleware, request_id_var

        async def echo_handler(request):
            return JSONResponse({"request_id": request_id_var.get()})

        app = Starlette(routes=[Route("/echo", echo_handler)])
        app.add_middleware(RequestIDMiddleware)
        return app

    def test_generates_uuid_when_no_header(self):
        client = TestClient(self._get_app())
        resp = client.get("/echo")
        assert "X-Request-ID" in resp.headers
        rid = resp.headers["X-Request-ID"]
        uuid.UUID(rid)

    def test_preserves_existing_request_id(self):
        client = TestClient(self._get_app())
        custom_id = str(uuid.uuid4())
        resp = client.get("/echo", headers={"X-Request-ID": custom_id})
        assert resp.headers["X-Request-ID"] == custom_id

    def test_request_id_available_in_handler(self):
        client = TestClient(self._get_app())
        resp = client.get("/echo")
        body = resp.json()
        assert body["request_id"] is not None
        uuid.UUID(body["request_id"])

    def test_different_requests_get_different_ids(self):
        client = TestClient(self._get_app())
        r1 = client.get("/echo")
        r2 = client.get("/echo")
        assert r1.headers["X-Request-ID"] != r2.headers["X-Request-ID"]
