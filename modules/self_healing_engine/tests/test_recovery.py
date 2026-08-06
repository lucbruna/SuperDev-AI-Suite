"""Tests for recovery: snapshots, persistence and rollback."""
from __future__ import annotations

from modules.self_healing_engine.recovery import (
    RollbackManager,
    SnapshotManager,
)
from modules.self_healing_engine.tests.helpers import make_context


def test_snapshot_create_and_list_most_recent_first() -> None:
    ctx = make_context()
    manager = SnapshotManager()
    manager.create("state", ctx, {"a": 1})
    manager.create("state", ctx, {"b": 2})

    snapshots = manager.list()
    assert len(snapshots) == 2
    assert snapshots[0].data == {"b": 2}  # most recent first
    assert manager.latest("state").id == "state-2"


def test_snapshot_retention_limit() -> None:
    ctx = make_context()
    from modules.self_healing_engine.config.recovery_config import RecoveryConfig

    manager = SnapshotManager(RecoveryConfig(max_checkpoints=3))
    for _ in range(5):
        manager.create("state", ctx, {})

    assert len(manager.list()) == 3


def test_snapshot_persistence_round_trip(tmp_path) -> None:
    ctx = make_context()
    manager = SnapshotManager()
    manager.create("state", ctx, {"k": "v"})
    path = tmp_path / "snapshots.json"
    manager.save_all(path)

    loaded = SnapshotManager()
    loaded.load_all(path)
    assert len(loaded.list()) == 1
    assert loaded.latest("state").data == {"k": "v"}


def test_snapshot_load_missing_raises() -> None:
    ctx = make_context()
    manager = SnapshotManager()
    try:
        manager.load("nope-1")
    except KeyError:
        pass
    else:
        raise AssertionError("missing snapshot should raise KeyError")


def test_rollback_manager_restores_artifact() -> None:
    ctx = make_context()
    manager = SnapshotManager()
    snapshot = manager.create("state", ctx, {"x": 1})
    rollback = RollbackManager(manager)

    assert rollback.rollback(snapshot, ctx) is True
    artifact = ctx.get_artifact("rollback_snapshot")
    assert artifact is not None
    assert artifact["id"] == snapshot.id


def test_rollback_latest_without_snapshot_returns_false() -> None:
    ctx = make_context()
    rollback = RollbackManager(SnapshotManager())
    assert rollback.rollback_latest(ctx) is False
