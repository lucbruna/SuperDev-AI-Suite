"""
Security Logger
"""
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class LogEntry:
    level: str
    message: str
    source: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    user_id: Optional[str] = None
    ip_address: Optional[str] = None


class SecurityLogger:
    def __init__(self):
        self.entries: List[LogEntry] = []
        self.max_entries: int = 50000
        self.min_level: str = "info"
        
    def log(self, level: str, message: str, source: str = "", **kwargs) -> LogEntry:
        entry = LogEntry(level=level, message=message, source=source, details=kwargs)
        self.entries.append(entry)
        if len(self.entries) > self.max_entries:
            self.entries = self.entries[-self.max_entries:]
        return entry
        
    def debug(self, message: str, source: str = "", **kwargs) -> LogEntry:
        return self.log("debug", message, source, **kwargs)
        
    def info(self, message: str, source: str = "", **kwargs) -> LogEntry:
        return self.log("info", message, source, **kwargs)
        
    def warning(self, message: str, source: str = "", **kwargs) -> LogEntry:
        return self.log("warning", message, source, **kwargs)
        
    def error(self, message: str, source: str = "", **kwargs) -> LogEntry:
        return self.log("error", message, source, **kwargs)
        
    def critical(self, message: str, source: str = "", **kwargs) -> LogEntry:
        return self.log("critical", message, source, **kwargs)
        
    def audit(self, action: str, user_id: str, resource: str = "", **kwargs) -> LogEntry:
        return self.log("audit", action, "audit", user_id=user_id, resource=resource, **kwargs)
        
    def get_by_level(self, level: str) -> List[LogEntry]:
        return [e for e in self.entries if e.level == level]
        
    def get_by_source(self, source: str) -> List[LogEntry]:
        return [e for e in self.entries if e.source == source]
        
    def get_recent(self, count: int = 100) -> List[LogEntry]:
        return self.entries[-count:]
        
    def count(self) -> int:
        return len(self.entries)
        
    def clear(self) -> None:
        self.entries.clear()
        
    def export_json(self) -> str:
        return json.dumps([
            {"level": e.level, "message": e.message, "source": e.source, "timestamp": e.timestamp.isoformat()}
            for e in self.entries
        ])
