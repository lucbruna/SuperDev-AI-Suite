"""Manager for database migrations."""
from typing import List, Dict, Any, Optional
from datetime import datetime
from .models import Migration, MigrationStep, MigrationStatus


class MigrationManager:
    """Manages database migration lifecycle."""

    def __init__(self):
        self._migrations: List[Migration] = []
        self._executed: List[Dict[str, Any]] = []

    def create_migration(self, name: str, steps: List[Dict[str, Any]]) -> Migration:
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
            version=f"{len(self._migrations)+1}.0.0",
        )
        self._migrations.append(migration)
        return migration

    def execute_migration(self, migration: Migration) -> bool:
        migration.status = MigrationStatus.RUNNING
        migration.executed_at = datetime.utcnow()
        try:
            for step in migration.steps:
                self._executed.append({
                    "migration_id": migration.migration_id,
                    "step_id": step.step_id,
                    "operation": step.operation,
                    "timestamp": datetime.utcnow().isoformat(),
                })
            migration.status = MigrationStatus.COMPLETED
            return True
        except Exception:
            migration.status = MigrationStatus.FAILED
            return False

    def rollback_migration(self, migration: Migration) -> bool:
        migration.status = MigrationStatus.ROLLED_BACK
        return True

    def get_pending(self) -> List[Migration]:
        return [m for m in self._migrations if m.status == MigrationStatus.PENDING]

    def get_executed(self) -> List[Migration]:
        return [m for m in self._migrations if m.status == MigrationStatus.COMPLETED]

    def get_all(self) -> List[Migration]:
        return list(self._migrations)

    def get_history(self) -> List[Dict[str, Any]]:
        return list(self._executed)
