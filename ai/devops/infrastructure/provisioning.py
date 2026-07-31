"""Provisioning."""
from __future__ import annotations
from typing import Any, Dict, List
import time

class ProvisioningEngine:
    def __init__(self) -> None:
        self._templates: Dict[str, Dict[str, Any]] = {}
        self._provisions: List[Dict[str, Any]] = []
    def create_template(self, name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        self._templates[name] = config
        return {"name": name, "created": True}
    def provision(self, template_name: str, overrides: Dict[str, Any] = None) -> Dict[str, Any]:
        template = self._templates.get(template_name, {})
        config = {**template, **(overrides or {})}
        import uuid
        pid = str(uuid.uuid4())[:8]
        provision = {"provision_id": pid, "template": template_name, "config": config, "status": "provisioned", "timestamp": time.time()}
        self._provisions.append(provision)
        return provision
    def deprovision(self, provision_id: str) -> bool:
        for p in self._provisions:
            if p["provision_id"] == provision_id:
                p["status"] = "deprovisioned"
                return True
        return False
    def list_templates(self) -> List[str]:
        return list(self._templates.keys())
    def list_provisions(self) -> List[Dict[str, Any]]:
        return self._provisions
    def count(self) -> int:
        return len(self._provisions)
