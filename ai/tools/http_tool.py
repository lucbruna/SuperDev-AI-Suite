from __future__ import annotations

from typing import Any

from security.ssrf import validate_public_url

from ..base.base_tool import BaseTool


class HTTPTool(BaseTool):
    _name = "http"
    _description = "Make HTTP requests to remote servers"
    _permissions = ["network"]

    def name(self) -> str:
        return self._name

    def description(self) -> str:
        return self._description

    def permissions(self) -> list[str]:
        return self._permissions

    async def validate(self, params: dict[str, Any]) -> bool:
        url = params.get("url")
        method = params.get("method", "GET")
        if not url or not isinstance(url, str):
            return False
        return method.upper() in ("GET", "POST", "PUT", "PATCH", "DELETE", "HEAD")

    async def execute(self, params: dict[str, Any]) -> dict[str, Any]:
        url = params.get("url", "")
        method = params.get("method", "GET").upper()
        headers = params.get("headers", {})
        body = params.get("body")
        timeout = params.get("timeout", 30)

        # SSRF guard (CWE-918): refuse private/loopback/metadata targets.
        try:
            validate_public_url(url)
        except ValueError as exc:
            return {"success": False, "error": str(exc)}

        try:
            import httpx
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.request(method, url, headers=headers, content=body)
                return {
                    "success": response.is_success,
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "body": response.text,
                    "elapsed": response.elapsed.total_seconds(),
                }
        except ImportError:
            try:
                import urllib.error
                import urllib.request
                req = urllib.request.Request(url, data=body.encode() if body else None, headers=headers, method=method)
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    return {
                        "success": True,
                        "status_code": resp.status,
                        "headers": dict(resp.headers),
                        "body": resp.read().decode("utf-8", errors="replace"),
                    }
            except Exception as e:
                return {"success": False, "error": str(e)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def rollback(self) -> None:
        pass

    async def cleanup(self) -> None:
        pass
