"""IP filtering."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
from enum import Enum
import time, uuid

class IPAction(Enum):
    ALLOW = "allow"
    DENY = "deny"
    RATE_LIMIT = "rate_limit"
    LOG = "log"

class IPFilter:
    def __init__(self) -> None:
        self._whitelist: set[str] = set()
        self._blacklist: set[str] = set()
        self._rate_limits: Dict[str, List[float]] = {}
        self._geo_blocks: Dict[str, str] = {}
    def allow(self, ip: str) -> None:
        self._whitelist.add(ip)
        self._blacklist.discard(ip)
    def deny(self, ip: str) -> None:
        self._blacklist.add(ip)
        self._whitelist.discard(ip)
    def remove(self, ip: str) -> None:
        self._whitelist.discard(ip)
        self._blacklist.discard(ip)
    def check(self, ip: str) -> IPAction:
        if ip in self._blacklist:
            return IPAction.DENY
        if ip in self._whitelist:
            return IPAction.ALLOW
        return IPAction.ALLOW
    def is_blocked(self, ip: str) -> bool:
        return ip in self._blacklist
    def is_allowed(self, ip: str) -> bool:
        return ip in self._whitelist
    def block_country(self, country_code: str) -> None:
        self._geo_blocks[country_code] = "blocked"
    def unblock_country(self, country_code: str) -> bool:
        if country_code in self._geo_blocks:
            del self._geo_blocks[country_code]
            return True
        return False
    def check_geo(self, country_code: str) -> bool:
        return country_code not in self._geo_blocks
    def list_whitelist(self) -> List[str]:
        return sorted(self._whitelist)
    def list_blacklist(self) -> List[str]:
        return sorted(self._blacklist)
    def list_blocked_countries(self) -> List[str]:
        return sorted(self._geo_blocks.keys())
