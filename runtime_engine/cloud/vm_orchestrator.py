from __future__ import annotations

import asyncio
import os
import uuid
from datetime import datetime
from typing import Any

import httpx


class VMOrchestrator:
    def __init__(self, provider: str = "aws"):
        self.provider = provider
        self._vms: dict[str, dict[str, Any]] = {}
        self._api_key = os.getenv(f"{provider.upper()}_API_KEY", "")
        self._region = os.getenv(f"{provider.upper()}_REGION", "us-east-1")

    async def create_vm(self, name: str, spec: dict[str, Any] | None = None) -> dict[str, Any]:
        vm_id = f"vm_{uuid.uuid4().hex[:12]}"
        config = {
            "cpu": (spec or {}).get("cpu", 2),
            "memory_gb": (spec or {}).get("memory_gb", 4),
            "disk_gb": (spec or {}).get("disk_gb", 20),
            "image": (spec or {}).get("image", "ubuntu:22.04"),
            "preemptible": (spec or {}).get("preemptible", True),
        }
        self._vms[vm_id] = {
            "id": vm_id,
            "name": name,
            "provider": self.provider,
            "region": self._region,
            "spec": config,
            "status": "provisioning",
            "ip": None,
            "created_at": datetime.utcnow().isoformat(),
            "agent_id": None,
        }
        asyncio.create_task(self._provision_vm(vm_id))
        return self._vms[vm_id]

    async def _provision_vm(self, vm_id: str) -> None:
        await asyncio.sleep(0.5)
        self._vms[vm_id]["status"] = "running"
        self._vms[vm_id]["ip"] = f"10.0.1.{hash(vm_id) % 254 + 1}"

    async def stop_vm(self, vm_id: str) -> bool:
        vm = self._vms.get(vm_id)
        if not vm or vm["status"] == "stopped":
            return False
        vm["status"] = "stopping"
        await asyncio.sleep(0.3)
        vm["status"] = "stopped"
        return True

    async def start_vm(self, vm_id: str) -> bool:
        vm = self._vms.get(vm_id)
        if not vm or vm["status"] != "stopped":
            return False
        vm["status"] = "provisioning"
        await asyncio.sleep(0.5)
        vm["status"] = "running"
        return True

    async def destroy_vm(self, vm_id: str) -> bool:
        vm = self._vms.pop(vm_id, None)
        return vm is not None

    async def attach_agent(self, vm_id: str, agent_id: str) -> bool:
        vm = self._vms.get(vm_id)
        if not vm:
            return False
        vm["agent_id"] = agent_id
        vm["status"] = "occupied"
        return True

    async def detach_agent(self, vm_id: str) -> bool:
        vm = self._vms.get(vm_id)
        if not vm:
            return False
        vm["agent_id"] = None
        vm["status"] = "running"
        return True

    async def execute_command(self, vm_id: str, command: str) -> dict[str, Any]:
        vm = self._vms.get(vm_id)
        if not vm or vm["status"] not in ("running", "occupied"):
            return {"error": "VM not available"}
        return {
            "vm_id": vm_id,
            "command": command,
            "stdout": f"$ {command}\nExecuted on {vm.get('ip', 'unknown')}",
            "stderr": "",
            "exit_code": 0,
        }

    async def list_vms(self, status: str | None = None) -> list[dict[str, Any]]:
        vms = list(self._vms.values())
        if status:
            vms = [v for v in vms if v["status"] == status]
        return vms

    async def get_vm(self, vm_id: str) -> dict[str, Any] | None:
        return self._vms.get(vm_id)

    async def get_vm_stats(self) -> dict[str, Any]:
        statuses = {}
        for vm in self._vms.values():
            s = vm["status"]
            statuses[s] = statuses.get(s, 0) + 1
        return {
            "total": len(self._vms),
            "by_status": statuses,
            "provider": self.provider,
            "region": self._region,
        }