"""Marketplace connector installation."""

from __future__ import annotations

import logging
from typing import Any

from .listing import MarketplaceListing


class MarketplaceInstaller:
    """Installs marketplace connectors into the platform."""

    def __init__(self, listing: MarketplaceListing) -> None:
        self._log = logging.getLogger("superdev.integration.marketplace.install")
        self._listing = listing
        self._installed: dict[str, dict[str, Any]] = {}

    def install(self, listing_id: str, config: dict[str, Any] | None = None) -> dict[str, Any]:
        listing = self._listing.get(listing_id)
        if not listing["published"]:
            raise ValueError(f"listing {listing_id!r} is not published")
        self._listing.increment_installs(listing_id)
        record = {
            "listing_id": listing_id,
            "name": listing["name"],
            "version": listing["version"],
            "config": config or {},
            "status": "installed",
        }
        self._installed[listing_id] = record
        self._log.info("installed connector %s", listing_id)
        return record

    def uninstall(self, listing_id: str) -> bool:
        return self._installed.pop(listing_id, None) is not None

    def is_installed(self, listing_id: str) -> bool:
        return listing_id in self._installed

    def list_installed(self) -> list[dict[str, Any]]:
        return list(self._installed.values())
