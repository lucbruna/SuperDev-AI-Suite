from __future__ import annotations

import hashlib
import os
import time
from typing import Any

from ..database_interfaces import IDatabaseDriver, IMigrationEngine, IMigrationHistory
from ..database_models import MigrationInfo, MigrationStatus, QueryResult


class MigrationHistory(IMigrationHistory):
    """Tracks applied migrations using a ``_migrations`` table."""

    def __init__(self, driver: IDatabaseDriver) -> None:
        self._driver = driver

    async def record(self, migration: MigrationInfo) -> None:
        q = (
            "INSERT INTO _migrations (id, name, version, status, executed_at, duration_ms, checksum) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)"
        )
        await self._driver.execute(q, [
            migration.id, migration.name, migration.version,
            migration.status.value, migration.executed_at or 0,
            migration.duration_ms, migration.checksum,
        ])

    async def get_applied(self) -> list[MigrationInfo]:
        q = "SELECT * FROM _migrations WHERE status = 'applied' ORDER BY version ASC"
        result = await self._driver.execute_query(q)
        return [MigrationInfo(
            id=r["id"], name=r["name"], version=r["version"],
            status=MigrationStatus(r["status"]),
            executed_at=r["executed_at"], duration_ms=r["duration_ms"],
            checksum=r["checksum"],
        ) for r in result]

    async def is_applied(self, migration_id: str) -> bool:
        q = "SELECT 1 FROM _migrations WHERE id = ? AND status = 'applied'"
        result = await self._driver.execute_query(q, [migration_id])
        return len(result) > 0


class MigrationEngine(IMigrationEngine):
    """Migration engine that discovers and runs SQL migration files."""

    def __init__(
        self,
        driver: IDatabaseDriver,
        migrations_dir: str = "migrations",
        history: IMigrationHistory | None = None,
    ) -> None:
        self._driver = driver
        self._migrations_dir = migrations_dir
        self._history = history or MigrationHistory(driver)

    async def create(self, name: str) -> str:
        migration_id = f"{int(time.time())}_{name}"
        up_path = os.path.join(self._migrations_dir, f"{migration_id}_up.sql")
        down_path = os.path.join(self._migrations_dir, f"{migration_id}_down.sql")
        os.makedirs(self._migrations_dir, exist_ok=True)
        for path in (up_path, down_path):
            if not os.path.exists(path):
                with open(path, "w") as f:
                    f.write(f"-- {os.path.basename(path)}\n")
        return migration_id

    async def run(self, target: str | None = None) -> list[MigrationInfo]:
        applied = []
        migrations = await self._discover_migrations()
        for mig in migrations:
            if mig.status == MigrationStatus.APPLIED:
                continue
            up_path = os.path.join(self._migrations_dir, f"{mig.id}_up.sql")
            if not os.path.exists(up_path):
                continue
            start = time.monotonic()
            try:
                with open(up_path) as f:
                    sql = f.read().strip()
                if sql:
                    await self._driver.execute(sql)
                mig.status = MigrationStatus.APPLIED
                mig.executed_at = time.time()
                mig.duration_ms = round((time.monotonic() - start) * 1000, 2)
                await self._history.record(mig)
                applied.append(mig)
            except Exception as exc:
                mig.status = MigrationStatus.FAILED
                mig.duration_ms = round((time.monotonic() - start) * 1000, 2)
                await self._history.record(mig)
                raise RuntimeError(f"Migration {mig.id} failed: {exc}") from exc
        return applied

    async def rollback(self, steps: int = 1) -> list[MigrationInfo]:
        rolled = []
        applied = await self._history.get_applied()
        for mig in reversed(applied[-steps:]):
            down_path = os.path.join(self._migrations_dir, f"{mig.id}_down.sql")
            if not os.path.exists(down_path):
                continue
            start = time.monotonic()
            try:
                with open(down_path) as f:
                    sql = f.read().strip()
                if sql:
                    await self._driver.execute(sql)
                mig.status = MigrationStatus.ROLLED_BACK
                mig.duration_ms = round((time.monotonic() - start) * 1000, 2)
                rolled.append(mig)
            except Exception as exc:
                raise RuntimeError(f"Rollback {mig.id} failed: {exc}") from exc
        return rolled

    async def history(self) -> list[MigrationInfo]:
        return await self._history.get_applied()

    async def _discover_migrations(self) -> list[MigrationInfo]:
        if not os.path.isdir(self._migrations_dir):
            return []
        migrations: list[MigrationInfo] = []
        seen: set[str] = set()
        for fname in sorted(os.listdir(self._migrations_dir)):
            if fname.endswith("_up.sql"):
                mig_id = fname[:-7]
                seen.add(mig_id)
        applied_set = {m.id for m in await self._history.get_applied()}
        for mig_id in sorted(seen):
            status = MigrationStatus.APPLIED if mig_id in applied_set else MigrationStatus.PENDING
            parts = mig_id.split("_", 1)
            version = parts[0] if len(parts) > 1 else mig_id
            migrations.append(MigrationInfo(
                id=mig_id,
                name=mig_id,
                version=version,
                status=status,
            ))
        return migrations


__all__ = [
    "MigrationEngine",
    "MigrationHistory",
]
