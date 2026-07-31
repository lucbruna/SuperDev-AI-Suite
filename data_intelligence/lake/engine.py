"""Lake engine (attached by the facade as ``lake``).

Stores raw and curated data in zones with partitioning and a catalog.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable

from data_intelligence.data_events import DataIntelligenceEvents
from data_intelligence.data_logger import get_logger
from data_intelligence.data_metrics import DataIntelligenceMetrics
from data_intelligence.data_protocols import new_id
from data_intelligence.lake.base import LakeZone
from data_intelligence.lake.catalog import LakeCatalog, LakeEntry
from data_intelligence.lake.compression import Compressor
from data_intelligence.lake.partition import DatePartitioner


class LakeEngine:
    """Coordinates lake zones, partitioning and the catalog."""

    ZONES = ("raw", "cleansed", "curated")

    def __init__(self, events: DataIntelligenceEvents,
                 metrics: DataIntelligenceMetrics, config: Any,
                 context: Any) -> None:
        self._log = get_logger()
        self.events = events
        self.metrics = metrics
        self.config = config
        self.context = context
        self.zones: dict[str, LakeZone] = {name: LakeZone(name)
                                           for name in self.ZONES}
        self.catalog = LakeCatalog()
        self.partitioner = DatePartitioner("day")

    # -- zones -------------------------------------------------------------
    def zone(self, name: str) -> LakeZone:
        zone = self.zones.get(name)
        if zone is None:
            raise ValueError(f"unknown lake zone: {name}")
        return zone

    def write(self, records: Iterable[dict[str, Any]],
              destination: Any) -> dict[str, Any]:
        """DataSink-compatible: stores a batch under ``destination``."""
        return self.store(list(records), zone=destination or "raw")

    def store(self, records: list[dict[str, Any]], zone: str = "raw",
              partition: str | None = None,
              compress: bool = True) -> dict[str, Any]:
        """Stores a batch of records as one object in a zone."""
        target = self.zone(zone)
        key = partition or self.partitioner.partition_key(datetime.now())
        object_id = new_id("obj")
        blob = Compressor.dumps(records)
        target.put(f"{key}/{object_id}", {"records": records},
                   compress=compress)
        meta = {"object_id": object_id, "zone": zone, "partition": key,
                "records": len(records),
                "size_bytes": len(blob)}
        self.catalog.add(LakeEntry(key=f"{key}/{object_id}", zone=zone,
                                   size_bytes=len(blob),
                                   compressed=compress, partition=key))
        self.metrics.increment(f"lake.writes.{zone}")
        return meta

    def read(self, object_id: str, zone: str = "raw") -> Any:
        """Reads a stored object by its id."""
        target = self.zone(zone)
        for key in target.keys():
            if object_id in key:
                data = target.get(key)
                return data.get("records", data)
        raise ValueError(f"object not found: {object_id}")

    def partition(self, name: str, zone: str, date_value: Any,
                  records: list[dict[str, Any]]) -> dict[str, Any]:
        """Stores records under a date partition."""
        key = self.partitioner.object_key(name, date_value)
        return self.store(records, zone=zone, partition=key)

    def stats(self) -> dict[str, Any]:
        return {"catalog": self.catalog.stats(),
                "zones": {name: zone.size()
                          for name, zone in self.zones.items()}}
