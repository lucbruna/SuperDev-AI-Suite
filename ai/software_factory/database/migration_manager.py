"""Manager for database migrations."""

from datetime import datetime
from typing import Any

from .models import Migration, MigrationStatus, MigrationStep


class MigrationManager:
    """Manages database migration lifecycle."""

    def __init__(self):
        self._migrations: list[Migration] = []
        self._executed: list[dict[str, Any]] = []

    def create_migration(self, name: str, steps: list[dict[str, Any]]) -> Migration:
        migration_steps = [
            MigrationStep(
                operation=s.get("operation", ""),
                table_name=s.get("table", ""),
                sql=s.get("sql", ""),
            )
            for s in steps
        ]
        migration = Migration(
            name=name,
            steps=migration_steps,
            version=f"{len(self._migrations) + 1}.0.0",
        )
        self._migrations.append(migration)
        return migration

    def execute_migration(self, migration: Migration) -> bool:
        migration.status = MigrationStatus.RUNNING
        migration.executed_at = datetime.utcnow()
        try:
            for step in migration.steps:
                self._executed.append(
                    {
                        "migration_id": migration.migration_id,
                        "step_id": step.step_id,
                        "operation": step.operation,
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                )
            migration.status = MigrationStatus.COMPLETED
            return True
        except Exception:
            migration.status = MigrationStatus.FAILED
            return False

    def rollback_migration(self, migration: Migration) -> bool:
        migration.status = MigrationStatus.ROLLED_BACK
        return True

    def get_pending(self) -> list[Migration]:
        return [m for m in self._migrations if m.status == MigrationStatus.PENDING]

    def get_executed(self) -> list[Migration]:
        return [m for m in self._migrations if m.status == MigrationStatus.COMPLETED]

    def get_all(self) -> list[Migration]:
        return list(self._migrations)

    def get_history(self) -> list[dict[str, Any]]:
        return list(self._executed)
