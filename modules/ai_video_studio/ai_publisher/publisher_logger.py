"""Publisher Logger — structured JSONL event logging for publishing (Volume 7)."""
from __future__ import annotations

import json
import logging
import time
import uuid

logger = logging.getLogger(__name__)


class PublisherLogger:
    """Append structured JSON events to a JSONL file under the downloads dir."""

    def __init__(self) -> None:
        self._file = None
        self._events: list[dict] = []

    def _ensure_file(self):
        if self._file is not None:
            return self._file
        try:
            from modules.ai_video_studio.media.output_paths import get_subsystem_dir

            directory = get_subsystem_dir("publish")
            self._file = directory / "publisher_events.jsonl"
            self._file.parent.mkdir(parents=True, exist_ok=True)
        except Exception:  # noqa: BLE001 — logging must never break publishing
            self._file = None
        return self._file

    def log(self, *, event: str, **fields) -> dict:
        """Write one structured event."""
        entry = {
            "id": uuid.uuid4().hex[:12],
            "ts": time.time(),
            "event": event,
            **fields,
        }
        self._events.append(entry)
        path = self._ensure_file()
        if path is not None:
            try:
                with path.open("a", encoding="utf-8") as fh:
                    fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
            except OSError as exc:  # noqa: BLE001
                logger.warning("Could not write publisher event: %s", exc)
        return entry

    def recent(self, *, limit: int = 50) -> list[dict]:
        return list(reversed(self._events[-limit:]))

    def stats(self) -> dict[str, int]:
        return {"events": len(self._events)}


_LOGGER: PublisherLogger | None = None


def get_publisher_logger() -> PublisherLogger:
    """Get the module-level singleton event logger."""
    global _LOGGER
    if _LOGGER is None:
        _LOGGER = PublisherLogger()
    return _LOGGER
