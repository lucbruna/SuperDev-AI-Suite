"""Queue Manager - Offline action queue management."""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import hashlib


class QueuePriority(Enum):
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


class QueueItemStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class QueueItem:
    item_id: str
    action: str
    payload: Dict[str, Any] = field(default_factory=dict)
    priority: QueuePriority = QueuePriority.NORMAL
    status: QueueItemStatus = QueueItemStatus.PENDING
    attempts: int = 0
    max_retries: int = 3
    created_at: datetime = field(default_factory=datetime.now)
    processed_at: Optional[datetime] = None


class OfflineQueueManager:
    def __init__(self):
        self.items: Dict[str, QueueItem] = {}
        self.order: List[str] = []

    def enqueue(self, action: str, payload: Dict[str, Any] = None, priority: QueuePriority = QueuePriority.NORMAL) -> QueueItem:
        item_id = hashlib.sha256(f"{action}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        item = QueueItem(item_id=item_id, action=action, payload=payload or {}, priority=priority)
        self.items[item_id] = item
        self.order.append(item_id)
        self.order.sort(key=lambda x: self.items[x].priority.value, reverse=True)
        return item

    def dequeue(self) -> Optional[QueueItem]:
        for item_id in self.order:
            item = self.items.get(item_id)
            if item and item.status == QueueItemStatus.PENDING:
                item.status = QueueItemStatus.PROCESSING
                return item
        return None

    def complete(self, item_id: str) -> bool:
        item = self.items.get(item_id)
        if item:
            item.status = QueueItemStatus.COMPLETED
            item.processed_at = datetime.now()
            return True
        return False

    def fail(self, item_id: str) -> bool:
        item = self.items.get(item_id)
        if item:
            item.attempts += 1
            if item.attempts >= item.max_retries:
                item.status = QueueItemStatus.FAILED
            else:
                item.status = QueueItemStatus.PENDING
            return True
        return False

    def get_pending(self) -> List[QueueItem]:
        return [self.items[iid] for iid in self.order if self.items.get(iid) and self.items[iid].status == QueueItemStatus.PENDING]

    def count(self) -> int:
        return len(self.items)

    def clear_completed(self) -> int:
        completed = [iid for iid, item in self.items.items() if item.status == QueueItemStatus.COMPLETED]
        for iid in completed:
            del self.items[iid]
            self.order.remove(iid)
        return len(completed)
