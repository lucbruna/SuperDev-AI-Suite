from __future__ import annotations


class MemoryError(Exception):
    """Base exception for the memory subsystem."""


class MemoryNotFoundError(MemoryError):
    """Requested memory entry does not exist."""


class MemoryFullError(MemoryError):
    """Memory storage has reached its capacity limit."""


class MemoryPermissionError(MemoryError):
    """Insufficient permissions for the requested memory operation."""


class MemoryValidationError(MemoryError):
    """Memory data failed validation."""


class MemorySecurityError(MemoryError):
    """Security violation detected in a memory operation."""


class MemoryCorruptionError(MemoryError):
    """Memory data is corrupted or inconsistent."""


class MemoryTimeoutError(MemoryError):
    """Memory operation exceeded its time limit."""


class MemoryBackupError(MemoryError):
    """Backup operation failed."""


class MemoryRestoreError(MemoryError):
    """Restore operation failed."""


class MemoryCheckpointError(MemoryError):
    """Checkpoint operation failed."""


class MemorySnapshotError(MemoryError):
    """Snapshot operation failed."""


class MemoryOptimizationError(MemoryError):
    """Optimization operation failed."""


class MemoryConflictError(MemoryError):
    """Concurrent modification conflict in memory."""


class MemoryLimitError(MemoryError):
    """Memory limit or quota exceeded."""
