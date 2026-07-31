"""Organization branding."""

from __future__ import annotations

from typing import Any


class BrandingManager:
    def __init__(self) -> None:
        self._branding: dict[str, dict[str, Any]] = {}

    def set(
        self,
        org_id: str,
        logo_url: str = "",
        primary_color: str = "#007bff",
        secondary_color: str = "#6c757d",
        custom_domain: str = "",
    ) -> dict[str, Any]:
        brand = {
            "org_id": org_id,
            "logo_url": logo_url,
            "primary_color": primary_color,
            "secondary_color": secondary_color,
            "custom_domain": custom_domain,
        }
        self._branding[org_id] = brand
        return brand

    def get(self, org_id: str) -> dict[str, Any]:
        return self._branding.get(org_id, {"primary_color": "#007bff", "secondary_color": "#6c757d"})

    def update(self, org_id: str, **kwargs: Any) -> dict[str, Any]:
        if org_id in self._branding:
            self._branding[org_id].update(kwargs)
            return self._branding[org_id]
        return self.set(org_id, **kwargs)

    def delete(self, org_id: str) -> bool:
        if org_id in self._branding:
            del self._branding[org_id]
            return True
        return False

    def list_all(self) -> dict[str, dict[str, Any]]:
        return dict(self._branding)
