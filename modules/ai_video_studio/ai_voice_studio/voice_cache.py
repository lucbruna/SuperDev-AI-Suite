"""Voice Cache — bounded LRU cache of synthesized clips on disk."""
from __future__ import annotations

import json
import logging
import os
from collections import OrderedDict
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_CACHE = None


def get_voice_cache() -> VoiceCache:
    global _CACHE
    if _CACHE is None:
        _CACHE = VoiceCache()
    return _CACHE


class VoiceCache:
    """Caches synthesis results keyed by (text, voice, language, prosody).

    Metadata lives in a JSON index under ``modules/downloads/voice/_cache.json``.
    """

    def __init__(self, max_entries: int = 128) -> None:
        self.max_entries = max_entries
        self._dir = Path(__file__).resolve().parent.parent.parent.parent / "downloads" / "voice"
        self._index_file = self._dir / "_cache.json"
        self._index: OrderedDict[str, dict[str, Any]] = OrderedDict()
        self._load()

    def _load(self) -> None:
        try:
            if self._index_file.exists():
                with open(self._index_file, encoding="utf-8") as f:
                    self._index = OrderedDict(json.load(f))
        except Exception as e:  # noqa: BLE001
            logger.warning("voice cache load failed: %s", e)

    def _save(self) -> None:
        try:
            self._dir.mkdir(parents=True, exist_ok=True)
            with open(self._index_file, "w", encoding="utf-8") as f:
                json.dump(list(self._index.items()), f)
        except Exception as e:  # noqa: BLE001
            logger.warning("voice cache save failed: %s", e)

    def get(self, key: str) -> dict[str, Any] | None:
        entry = self._index.get(key)
        if not entry or not os.path.exists(entry["output_path"]):
            return None
        self._index.move_to_end(key)
        return {**entry, "cached": True}

    def put(self, key: str, result: dict[str, Any]) -> None:
        self._index[key] = result
        self._index.move_to_end(key)
        while len(self._index) > self.max_entries:
            self._index.popitem(last=False)
        self._save()

    def clear(self) -> int:
        count = len(self._index)
        self._index.clear()
        self._save()
        return count

    def stats(self) -> dict[str, Any]:
        return {"entries": len(self._index), "max_entries": self.max_entries}
