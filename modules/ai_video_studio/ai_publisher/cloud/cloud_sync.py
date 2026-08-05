"""Cloud Sync — folder synchronization and diffing (Volume 7)."""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class CloudSync:
    """Compute differences between local and cloud states."""

    def diff(self, *, local: list[str], cloud: list[str]) -> dict:
        """Return objects that need upload, deletion, or are unchanged."""
        local_set, cloud_set = set(local), set(cloud)
        return {
            "to_upload": sorted(local_set - cloud_set),
            "to_delete": sorted(cloud_set - local_set),
            "unchanged": sorted(local_set & cloud_set),
        }

    def plan(self, *, local: list[str], cloud: list[str]) -> list[dict]:
        """Build an ordered sync plan."""
        d = self.diff(local=local, cloud=cloud)
        return (
            [{"action": "upload", "key": k} for k in d["to_upload"]]
            + [{"action": "delete", "key": k} for k in d["to_delete"]]
        )

    def stats(self) -> dict[str, int]:
        return {"operations": 2}


_SYNC: CloudSync | None = None


def get_cloud_sync() -> CloudSync:
    """Get the module-level singleton cloud sync."""
    global _SYNC
    if _SYNC is None:
        _SYNC = CloudSync()
    return _SYNC
