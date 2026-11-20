"""Crash-safe JSON persistence for the local video-studio workspace.

This store is intentionally file-backed and requires no database server. Nested
dict/list mutations are observed so existing CRUD handlers persist without
having to know about storage details.
"""
from __future__ import annotations

import json
import os
import threading
from pathlib import Path
from typing import Any, Callable


def _wrap(value: Any, changed: Callable[[], None]) -> Any:
    if isinstance(value, dict):
        return _TrackedDict(value, changed)
    if isinstance(value, list):
        return _TrackedList(value, changed)
    return value


class _TrackedDict(dict):
    def __init__(self, value: dict, changed: Callable[[], None]):
        self._changed = changed
        dict.__init__(self, {k: _wrap(v, changed) for k, v in value.items()})

    def __setitem__(self, key, value):
        dict.__setitem__(self, key, _wrap(value, self._changed))
        self._changed()

    def __delitem__(self, key):
        dict.__delitem__(self, key)
        self._changed()

    def update(self, *args, **kwargs):
        incoming = dict(*args, **kwargs)
        for key, value in incoming.items():
            dict.__setitem__(self, key, _wrap(value, self._changed))
        if incoming:
            self._changed()

    def clear(self):
        if self:
            dict.clear(self)
            self._changed()

    def pop(self, key, *args):
        value = dict.pop(self, key, *args)
        self._changed()
        return value

    def popitem(self):
        value = dict.popitem(self)
        self._changed()
        return value

    def setdefault(self, key, default=None):
        if key in self:
            return self[key]
        self[key] = default
        return self[key]


class _TrackedList(list):
    def __init__(self, values: list, changed: Callable[[], None]):
        self._changed = changed
        list.__init__(self, [_wrap(v, changed) for v in values])

    def append(self, value):
        list.append(self, _wrap(value, self._changed))
        self._changed()

    def extend(self, values):
        values = [_wrap(v, self._changed) for v in values]
        if values:
            list.extend(self, values)
            self._changed()

    def insert(self, index, value):
        list.insert(self, index, _wrap(value, self._changed))
        self._changed()

    def __setitem__(self, index, value):
        if isinstance(index, slice):
            value = [_wrap(v, self._changed) for v in value]
        else:
            value = _wrap(value, self._changed)
        list.__setitem__(self, index, value)
        self._changed()

    def __delitem__(self, index):
        list.__delitem__(self, index)
        self._changed()

    def pop(self, index=-1):
        value = list.pop(self, index)
        self._changed()
        return value

    def remove(self, value):
        list.remove(self, value)
        self._changed()

    def clear(self):
        if self:
            list.clear(self)
            self._changed()


class PersistentDict(dict):
    """A dict-compatible JSON store that persists top-level and nested changes."""

    def __init__(self, name: str, initial: dict | None = None):
        self._lock = threading.RLock()
        from modules.ai_video_studio.core.settings import get_settings

        root = Path(get_settings().storage.local_path).expanduser()
        self.path = root / "state" / f"{name}.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if self.path.exists():
            try:
                data = json.loads(self.path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                raise RuntimeError(f"Cannot read local workspace state {self.path}: {exc}") from exc
            if not isinstance(data, dict):
                raise RuntimeError(f"Local workspace state must be a JSON object: {self.path}")
        else:
            data = initial or {}
        dict.__init__(self)
        self._ready = False
        for key, value in data.items():
            dict.__setitem__(self, key, _wrap(value, self._save))
        self._ready = True
        if not self.path.exists():
            self._save()

    def _save(self):
        if not self._ready:
            return
        with self._lock:
            payload = json.dumps(self, ensure_ascii=False, indent=2)
            temp = self.path.with_suffix(self.path.suffix + ".tmp")
            temp.write_text(payload + "\n", encoding="utf-8")
            os.replace(temp, self.path)

    def __setitem__(self, key, value):
        dict.__setitem__(self, key, _wrap(value, self._save))
        self._save()

    def __delitem__(self, key):
        dict.__delitem__(self, key)
        self._save()

    def update(self, *args, **kwargs):
        incoming = dict(*args, **kwargs)
        for key, value in incoming.items():
            dict.__setitem__(self, key, _wrap(value, self._save))
        if incoming:
            self._save()

    def clear(self):
        if self:
            dict.clear(self)
            self._save()

    def pop(self, key, *args):
        value = dict.pop(self, key, *args)
        self._save()
        return value

    def popitem(self):
        value = dict.popitem(self)
        self._save()
        return value

    def setdefault(self, key, default=None):
        if key in self:
            return self[key]
        self[key] = default
        return self[key]
