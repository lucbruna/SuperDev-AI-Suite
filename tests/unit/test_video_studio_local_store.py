"""Tests for the local JSON workspace store."""
from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from modules.ai_video_studio.core import settings
from modules.ai_video_studio.core.local_store import PersistentDict


def _use_workspace(monkeypatch, tmp_path):
    monkeypatch.setattr(
        settings,
        "get_settings",
        lambda: SimpleNamespace(storage=SimpleNamespace(local_path=tmp_path)),
    )


def test_persistent_dict_restores_nested_dict_and_list_mutations(monkeypatch, tmp_path):
    _use_workspace(monkeypatch, tmp_path)
    store = PersistentDict("projects", {"project-1": {"name": "Initial", "clips": []}})

    store["project-1"].update({"name": "Edited"})
    store["project-1"]["clips"].append({"scene_id": "scene-1", "duration": 10})
    store["project-2"] = {"name": "Second"}

    restored = PersistentDict("projects")
    assert restored["project-1"]["name"] == "Edited"
    assert restored["project-1"]["clips"][0]["duration"] == 10
    assert restored["project-2"]["name"] == "Second"


def test_persistent_dict_persists_deletions(monkeypatch, tmp_path):
    _use_workspace(monkeypatch, tmp_path)
    store = PersistentDict("renders", {"render-1": {"status": "queued"}})

    del store["render-1"]

    assert PersistentDict("renders") == {}


def test_corrupt_workspace_state_fails_loudly(monkeypatch, tmp_path):
    _use_workspace(monkeypatch, tmp_path)
    state_dir = tmp_path / "state"
    state_dir.mkdir()
    (state_dir / "projects.json").write_text("{broken", encoding="utf-8")

    with pytest.raises(RuntimeError, match="Cannot read local workspace state"):
        PersistentDict("projects")


def test_workspace_state_is_valid_json_after_each_mutation(monkeypatch, tmp_path):
    _use_workspace(monkeypatch, tmp_path)
    store = PersistentDict("timelines", {"timeline-1": {"clips": []}})
    store["timeline-1"]["clips"].append({"scene_id": "s1"})

    saved = json.loads((tmp_path / "state" / "timelines.json").read_text(encoding="utf-8"))
    assert saved["timeline-1"]["clips"] == [{"scene_id": "s1"}]
