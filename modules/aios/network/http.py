"""Network HTTP — lightweight HTTP checks via stdlib urllib (Vol 12, Fase 27)."""
from __future__ import annotations

import urllib.error
import urllib.request
from time import monotonic
from typing import Any

from modules.aios.network.acl import require_network_action
from modules.aios.kernel.kernel_logger import get_kernel_logger
from modules.aios.kernel.kernel_metrics import get_kernel_metrics


class Http:
    """Performs HTTP HEAD/GET requests using the stdlib urllib client."""

    def __init__(self) -> None:
        self._logger = get_kernel_logger()
        self._metrics = get_kernel_metrics()

    def _request(self, url: str, method: str, timeout: float) -> dict[str, Any]:
        started = monotonic()
        req = urllib.request.Request(url, method=method)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                status = resp.status
                headers = dict(resp.headers.items())
        except urllib.error.HTTPError as exc:
            status = exc.code
            headers = dict(exc.headers.items())
        except (urllib.error.URLError, OSError) as exc:
            return {"ok": False, "url": url, "reason": str(exc)}
        self._metrics.record_timing("network.http", monotonic() - started)
        self._logger.log("network", f"http: {method} {url} -> {status}")
        return {"ok": True, "url": url, "status": status, "headers": headers}

    def head(self, url: str, *, timeout: float = 5.0) -> dict[str, Any]:
        require_network_action("http")
        return self._request(url, "HEAD", timeout)

    def get(self, url: str, *, timeout: float = 5.0) -> dict[str, Any]:
        require_network_action("http")
        return self._request(url, "GET", timeout)


__all__ = ["Http"]
