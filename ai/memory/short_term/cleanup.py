from __future__ import annotations

from .interaction_history import InteractionHistory
from .temporary_storage import TemporaryStorage
from .working_buffer import WorkingBuffer


class Cleanup:
    """Cleanup strategies for short-term memory."""

    def clean(
        self,
        temporary: TemporaryStorage,
        buffer: WorkingBuffer,
        history: InteractionHistory,
    ) -> int:
        count = 0
        count += temporary.purge_expired()
        buffer.clear()
        history.clear()
        count += 1
        return count

    def clear_all(
        self,
        temporary: TemporaryStorage,
        buffer: WorkingBuffer,
        history: InteractionHistory,
    ) -> int:
        count = temporary.count + buffer.size + history.length
        temporary.clear()
        buffer.clear()
        history.clear()
        return count
