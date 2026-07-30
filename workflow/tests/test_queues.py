from __future__ import annotations

from workflow.queues.queue_models import QueueItem, QueueStatus
from workflow.queues.queue_engine import QueueEngine
from workflow.queues.queue_priority import QueuePriority
from workflow.queues.queue_monitor import QueueMonitor


class TestQueues:
    def test_queue_item_defaults(self) -> None:
        item = QueueItem()
        assert item.status == QueueStatus.PENDING
        assert item.retries == 0

    def test_queue_enqueue_dequeue(self) -> None:
        engine = QueueEngine()
        engine.enqueue({"action": "test"})
        item = engine.dequeue()
        assert item is not None
        assert item.status == QueueStatus.PROCESSING

    def test_queue_fail_retry(self) -> None:
        engine = QueueEngine()
        item = engine.enqueue({"action": "test"})
        engine.fail(item.id, "error")
        assert item.status == QueueStatus.RETRYING

    def test_queue_fail_exhausted(self) -> None:
        engine = QueueEngine()
        item = engine.enqueue({"action": "test"})
        item.max_retries = 0
        engine.fail(item.id, "error")
        assert item.status == QueueStatus.FAILED

    def test_queue_priority(self) -> None:
        low = QueueItem(payload={"task": "low"}, priority=0)
        high = QueueItem(payload={"task": "high"}, priority=10)
        result = QueuePriority.highest([low, high])
        assert result == high

    def test_queue_monitor(self) -> None:
        monitor = QueueMonitor()
        report = monitor.status_report([QueueItem()])
        assert report["total"] == 1
        assert report["pending"] == 1
