from __future__ import annotations

import asyncio
import os
from typing import Any


class BrowserSession:
    def __init__(self, headless: bool = True):
        self.headless = headless
        self._sessions: dict[str, dict[str, Any]] = {}

    async def launch(self, url: str = "about:blank", width: int = 1280, height: int = 720) -> dict[str, Any]:
        session_id = f"browser_{len(self._sessions) + 1}"
        self._sessions[session_id] = {
            "id": session_id,
            "url": url,
            "viewport": {"width": width, "height": height},
            "status": "launched",
            "screenshot": None,
            "console_logs": [],
        }
        await asyncio.sleep(0.3)
        return self._sessions[session_id]

    async def navigate(self, session_id: str, url: str) -> dict[str, Any]:
        session = self._sessions.get(session_id)
        if not session:
            return {"error": "Session not found"}
        session["url"] = url
        await asyncio.sleep(0.2)
        return {"status": "navigated", "url": url, "title": url}

    async def screenshot(self, session_id: str) -> dict[str, Any]:
        session = self._sessions.get(session_id)
        if not session:
            return {"error": "Session not found"}
        return {"session_id": session_id, "screenshot": f"data:image/png;base64,{_mock_screenshot()}", "url": session["url"]}

    async def evaluate(self, session_id: str, script: str) -> dict[str, Any]:
        session = self._sessions.get(session_id)
        if not session:
            return {"error": "Session not found"}
        return {"result": f"<evaluated: {script[:50]}>"}

    async def get_html(self, session_id: str) -> dict[str, Any]:
        session = self._sessions.get(session_id)
        if not session:
            return {"error": "Session not found"}
        return {"html": f"<html><head><title>{session['url']}</title></head><body><h1>Mock content</h1></body></html>"}

    async def click(self, session_id: str, selector: str) -> dict[str, Any]:
        return {"status": "clicked", "selector": selector}

    async def type_text(self, session_id: str, selector: str, text: str) -> dict[str, Any]:
        return {"status": "typed", "selector": selector, "text": text[:50]}

    async def close(self, session_id: str) -> bool:
        return self._sessions.pop(session_id, None) is not None

    async def list_sessions(self) -> list[dict[str, Any]]:
        return list(self._sessions.values())


def _mock_screenshot() -> str:
    return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="