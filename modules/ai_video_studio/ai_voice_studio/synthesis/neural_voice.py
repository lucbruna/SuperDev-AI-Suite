"""Neural Voice — pluggable neural TTS endpoint (HTTP).

When ``AIVS_NEURAL_TTS_URL`` is set, synthesis POSTs to a neural TTS
service (e.g. a self-hosted Coqui/XTTS or cloud endpoint). Without a
configured endpoint the helper returns ``None`` and the caller falls back
to the standard chain — the studio never breaks on configuration gaps.
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

ENV_URL = "AIVS_NEURAL_TTS_URL"


class NeuralVoice:
    """Optional remote neural voice endpoint."""

    def __init__(self, url: str | None = None) -> None:
        self.url = url or os.getenv(ENV_URL, "").strip()

    @property
    def available(self) -> bool:
        return bool(self.url)

    async def synthesize(
        self, text: str, *, voice_id: str = "default", language: str = "en",
        output_path: str, timeout: float = 120.0,
    ) -> dict[str, Any] | None:
        """POST the text and save the returned audio; ``None`` when unavailable."""
        if not self.available:
            return None
        try:
            import urllib.request

            body = json.dumps(
                {"text": text, "voice_id": voice_id, "language": language, "response_format": "wav"}
            ).encode()
            req = urllib.request.Request(
                self.url.rstrip("/") + "/synthesize",
                data=body,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            async def _post() -> bytes:
                return await asyncio.to_thread(
                    lambda: urllib.request.urlopen(req, timeout=timeout).read()
                )

            data = await _post()
            if not data:
                return None
            out_dir = os.path.dirname(output_path)
            os.makedirs(out_dir, exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(data)
            return {"output_path": output_path, "engine": "neural", "bytes": len(data)}
        except Exception as e:  # noqa: BLE001
            logger.warning("neural TTS endpoint failed: %s", e)
            return None
