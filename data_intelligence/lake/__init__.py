"""Lake subsystem (Volume 22).

Raw, cleansed and curated data zones with partitioning, compression and a
catalog of every stored object.
"""

from __future__ import annotations

from data_intelligence.lake.base import LakeError, LakeZone
from data_intelligence.lake.catalog import LakeCatalog, LakeEntry
from data_intelligence.lake.compression import Compressor
from data_intelligence.lake.engine import LakeEngine
from data_intelligence.lake.partition import DatePartitioner

__all__ = [
    "LakeEngine", "LakeZone", "LakeCatalog", "LakeEntry", "Compressor",
    "DatePartitioner", "LakeError",
]
