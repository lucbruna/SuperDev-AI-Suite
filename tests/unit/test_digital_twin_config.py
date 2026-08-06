"""Unit tests for the Digital Twin configuration package."""
from __future__ import annotations

import pytest

from modules.digital_twin.config import (
    ENTITY_TYPES,
    ENV_PREFIX,
    PERMISSIONS,
    PHASES,
    RELATION_KINDS,
    RISK_LEVELS,
    ROLES,
    SYNC_KINDS,
    SYNC_STATUSES,
    TWIN_STATUSES,
    DigitalTwinConfig,
    Permissions,
)
from modules.digital_twin.config.constants import (
    PERM_MANAGE_TWIN,
    PERM_RUN_PREDICTION,
    PERM_RUN_SIMULATION,
    PERM_TRIGGER_SYNC,
    PERM_VIEW_TWIN,
    REL_DEPENDS_ON,
    ROLE_ADMIN,
    ROLE_OPERATOR,
    ROLE_VIEWER,
)
from modules.digital_twin.version import VERSION, __version__


class TestDigitalTwinConfig:
    def test_defaults(self) -> None:
        cfg = DigitalTwinConfig()
        assert cfg.name == "digital_twin"
        assert cfg.enabled is True
        assert cfg.snapshot_retention == 50
        assert cfg.simulation.enabled is True
        assert cfg.prediction.horizon_steps == 5
        assert cfg.sync.interval_seconds == 30
        assert cfg.monitoring.alert_threshold == 0.8
        assert cfg.memory.max_entries == 1000

    def test_from_env_overrides(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("SUPERDEV_DT_ENABLED", "false")
        monkeypatch.setenv("SUPERDEV_DT_SNAPSHOT_RETENTION", "7")
        monkeypatch.setenv("SUPERDEV_DT_SIM_MAX_SCENARIOS", "5")
        monkeypatch.setenv("SUPERDEV_DT_PRED_HORIZON_STEPS", "3")
        monkeypatch.setenv("SUPERDEV_DT_SYNC_INTERVAL_SECONDS", "10")
        monkeypatch.setenv("SUPERDEV_DT_MON_ANOMALY_WINDOW", "4")
        monkeypatch.setenv("SUPERDEV_DT_MEM_MAX_ENTRIES", "50")
        cfg = DigitalTwinConfig.from_env()
        assert cfg.enabled is False
        assert cfg.snapshot_retention == 7
        assert cfg.simulation.max_scenarios == 5
        assert cfg.prediction.horizon_steps == 3
        assert cfg.sync.interval_seconds == 10
        assert cfg.monitoring.anomaly_window == 4
        assert cfg.memory.max_entries == 50

    def test_from_env_invalid_values_fall_back(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("SUPERDEV_DT_SNAPSHOT_RETENTION", "nope")
        monkeypatch.setenv("SUPERDEV_DT_ENABLED", "maybe")
        cfg = DigitalTwinConfig.from_env()
        assert cfg.snapshot_retention == 50
        # Unknown bool values resolve to False (same semantics as AD module).
        assert cfg.enabled is False

    def test_from_env_unset_keeps_defaults(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("SUPERDEV_DT_ENABLED", raising=False)
        cfg = DigitalTwinConfig.from_env()
        assert cfg.enabled is True

    def test_resolve_sets_data_dir(self, tmp_path) -> None:
        cfg = DigitalTwinConfig()
        cfg.resolve(str(tmp_path))
        assert cfg.project_root == str(tmp_path.resolve())
        expected = str(tmp_path.resolve() / ".superdev" / "digital_twin")
        assert cfg.data_dir == expected

    def test_resolve_with_existing_data_dir(self, tmp_path) -> None:
        cfg = DigitalTwinConfig()
        custom = str(tmp_path / "custom")
        cfg.data_dir = custom
        cfg.resolve(str(tmp_path))
        assert cfg.data_dir == custom


class TestSimulationConfig:
    def test_env_prefix(self, monkeypatch: pytest.MonkeyPatch) -> None:
        assert ENV_PREFIX == "SUPERDEV_DT_"
        monkeypatch.setenv("SUPERDEV_DT_SIM_SEED", "1234")
        from modules.digital_twin.config import SimulationConfig

        cfg = SimulationConfig.from_env()
        assert cfg.seed == 1234


class TestPermissions:
    def test_viewer(self) -> None:
        p = Permissions.for_role(ROLE_VIEWER)
        assert p.can(PERM_VIEW_TWIN)
        assert not p.can(PERM_RUN_SIMULATION)
        assert not p.can(PERM_MANAGE_TWIN)

    def test_operator(self) -> None:
        p = Permissions.for_role(ROLE_OPERATOR)
        assert p.can(PERM_VIEW_TWIN)
        assert p.can(PERM_RUN_SIMULATION)
        assert p.can(PERM_RUN_PREDICTION)
        assert p.can(PERM_TRIGGER_SYNC)
        assert not p.can(PERM_MANAGE_TWIN)

    def test_admin(self) -> None:
        p = Permissions.for_role(ROLE_ADMIN)
        for perm in PERMISSIONS:
            assert p.can(perm)

    def test_unknown_role_falls_back_to_viewer(self) -> None:
        p = Permissions.for_role("root")
        assert p.role == ROLE_VIEWER
        assert not p.can(PERM_MANAGE_TWIN)

    def test_explicit_grants_are_additive(self) -> None:
        p = Permissions.for_role(ROLE_VIEWER)
        p2 = Permissions(role=ROLE_VIEWER, grants=frozenset({PERM_RUN_SIMULATION}))
        assert p2.can(PERM_RUN_SIMULATION)
        assert p2.can(PERM_VIEW_TWIN)
        assert not p.can(PERM_RUN_SIMULATION)

    def test_to_dict(self) -> None:
        p = Permissions.for_role(ROLE_ADMIN)
        d = p.to_dict()
        assert d["role"] == ROLE_ADMIN
        grants = d["grants"]
        assert isinstance(grants, list)
        assert PERM_MANAGE_TWIN in grants


class TestConstants:
    def test_lists_are_consistent(self) -> None:
        assert set(SYNC_KINDS) == {"full", "incremental"}
        assert set(SYNC_STATUSES) == {"pending", "running", "success", "failed", "skipped"}
        assert set(TWIN_STATUSES) == {"synced", "out_of_sync", "stale"}
        assert set(ROLES) == {ROLE_VIEWER, ROLE_OPERATOR, ROLE_ADMIN}
        assert set(PHASES) == {"sync", "simulate", "predict", "monitor", "report"}
        assert "project" in ENTITY_TYPES
        assert REL_DEPENDS_ON in RELATION_KINDS
        assert RISK_LEVELS[0] == "low"
        assert RISK_LEVELS[-1] == "critical"

    def test_version(self) -> None:
        assert VERSION == __version__
        assert __version__.count(".") == 2
