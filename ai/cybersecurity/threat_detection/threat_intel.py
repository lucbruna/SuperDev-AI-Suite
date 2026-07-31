"""
Threat Intelligence Management
"""

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class IOCType(Enum):
    IP_ADDRESS = "ip_address"
    DOMAIN = "domain"
    URL = "url"
    FILE_HASH = "file_hash"
    EMAIL = "email"
    CVE = "cve"


class ThreatLevel(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class IOC:
    ioc_id: str
    ioc_type: IOCType
    value: str
    threat_level: ThreatLevel = ThreatLevel.MEDIUM
    source: str = ""
    description: str = ""
    first_seen: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
    tags: list[str] = field(default_factory=list)
    confidence: float = 0.5


@dataclass
class ThreatFeed:
    feed_id: str
    name: str
    url: str = ""
    enabled: bool = True
    last_updated: datetime | None = None
    ioc_count: int = 0


class ThreatIntel:
    def __init__(self):
        self.iocs: dict[str, IOC] = {}
        self.feeds: dict[str, ThreatFeed] = {}
        self.correlations: dict[str, list[str]] = {}

    def add_ioc(
        self, ioc_type: IOCType, value: str, threat_level: ThreatLevel = ThreatLevel.MEDIUM, source: str = "", **kwargs
    ) -> IOC:
        ioc_id = hashlib.sha256(f"{ioc_type.value}:{value}".encode()).hexdigest()[:16]
        ioc = IOC(ioc_id=ioc_id, ioc_type=ioc_type, value=value, threat_level=threat_level, source=source, **kwargs)
        self.iocs[ioc_id] = ioc
        return ioc

    def lookup(self, value: str) -> IOC | None:
        for ioc in self.iocs.values():
            if ioc.value == value:
                return ioc
        return None

    def add_feed(self, name: str, url: str = "") -> ThreatFeed:
        feed_id = hashlib.sha256(name.encode()).hexdigest()[:16]
        feed = ThreatFeed(feed_id=feed_id, name=name, url=url)
        self.feeds[feed_id] = feed
        return feed

    def correlate(self, ioc_id: str, related_ids: list[str]) -> None:
        self.correlations[ioc_id] = related_ids

    def search(self, query: str) -> list[IOC]:
        return [
            ioc
            for ioc in self.iocs.values()
            if query.lower() in ioc.value.lower() or query.lower() in ioc.description.lower()
        ]

    def get_by_type(self, ioc_type: IOCType) -> list[IOC]:
        return [ioc for ioc in self.iocs.values() if ioc.ioc_type == ioc_type]

    def get_by_threat_level(self, level: ThreatLevel) -> list[IOC]:
        return [ioc for ioc in self.iocs.values() if ioc.threat_level == level]

    def get_recent(self, hours: int = 24) -> list[IOC]:
        cutoff = datetime.now()
        return [ioc for ioc in self.iocs.values() if (cutoff - ioc.first_seen).total_seconds() < hours * 3600]

    def count(self) -> int:
        return len(self.iocs)
