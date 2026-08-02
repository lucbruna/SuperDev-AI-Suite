"""Sandbox — one isolated execution environment composed from its layers."""
from __future__ import annotations
import asyncio
from time import monotonic
from typing import Any, Awaitable, Callable
from uuid import uuid4

from modules.aios.kernel.kernel_events import emit
from modules.aios.kernel.kernel_logger import get_kernel_logger
from modules.aios.sandbox.sandbox_limits import SandboxLimitError, SandboxLimits
from modules.aios.sandbox.sandbox_network import SandboxNetwork
from modules.aios.sandbox.sandbox_permissions import SandboxPermissions
from modules.aios.sandbox.sandbox_policy import SandboxPolicy
from modules.aios.sandbox.sandbox_storage import SandboxStorage

SandboxFn = Callable[..., Any]


class Sandbox:
    """Facade: policy + permissions + network + limits + storage.

    Lifecycle: ``created -> ready -> running -> closed``. ``close`` is
    idempotent and always tears down storage, even after a failed run.
    """

    def __init__(self, policy: SandboxPolicy, sandbox_id: str | None = None) -> None:
        self.id = sandbox_id or uuid4().hex
        self.policy = policy
        self.permissions = SandboxPermissions(self.id)
        self.network = SandboxNetwork(policy.network)
        self.limits = SandboxLimits(
            timeout_s=policy.timeout_s,
            max_memory_mb=policy.max_memory_mb,
            max_storage_mb=policy.max_storage_mb,
        )
        # Storage reports bytes written back to the limits layer so the
        # storage budget is enforced at write time (before it can overflow).
        self.storage = SandboxStorage(self.id, on_write=self.limits.record_storage)
        self._logger = get_kernel_logger()
        self._closed = False
        self._last_run: dict[str, Any] | None = None

        # Wire policy into the permission layer. Running is the sandbox's
        # fundamental operation and is always granted; risky capabilities
        # (fs_write, network, command) are opt-in via the policy.
        self.permissions.grant("run")
        if policy.allow_fs_write:
            self.permissions.grant("fs_write")
        if policy.network.value != "offline":
            self.permissions.grant("network")
        for command in policy.allowed_commands:
            self.permissions.grant("command")

    @property
    def closed(self) -> bool:
        return self._closed

    def require_action(self, action: str) -> None:
        self.permissions.require(action)

    async def run(self, fn: SandboxFn, *args: Any, **kwargs: Any) -> Any:
        """Execute ``fn`` under the sandbox's timeout budget."""
        if self._closed:
            raise RuntimeError(f"sandbox {self.id} is closed")
        self.require_action("run")

        started = monotonic()
        try:
            coro = fn(*args, **kwargs)
            if asyncio.iscoroutine(coro) or isinstance(coro, Awaitable):
                if self.limits.timeout_s is not None:
                    coro = asyncio.wait_for(coro, timeout=self.limits.timeout_s)
                result = await coro
            else:
                if self.limits.timeout_s is not None:
                    result = await asyncio.wait_for(
                        asyncio.to_thread(lambda: fn(*args, **kwargs)),
                        timeout=self.limits.timeout_s,
                    )
                else:
                    result = await asyncio.to_thread(fn, *args, **kwargs)
            self._last_run = {"ok": True}
            return result
        except (TimeoutError, SandboxLimitError):
            self._last_run = {"ok": False, "error": "timeout"}
            raise
        except Exception as e:  # noqa: BLE001
            self._last_run = {"ok": False, "error": str(e)}
            raise
        finally:
            # Accounting only — the timeout was already enforced during
            # execution via asyncio.wait_for. A successful run that took
            # slightly over budget must not fail in teardown.
            self.limits.record_elapsed(monotonic() - started)

    async def close(self) -> dict[str, Any]:
        if self._closed:
            return {"sandbox_id": self.id, "closed": True}
        self._closed = True
        self.storage.close()
        self._logger.log("sandbox", f"sandbox {self.id} closed")
        try:
            asyncio.get_running_loop().create_task(
                emit("sandbox.closed", sandbox_id=self.id, name=self.policy.name)
            )
        except RuntimeError:
            pass
        return {"sandbox_id": self.id, "closed": True}

    def snapshot(self) -> dict[str, Any]:
        return {
            "sandbox_id": self.id,
            "name": self.policy.name,
            "closed": self._closed,
            "policy": self.policy.snapshot(),
            "permissions": self.permissions.snapshot(),
            "network": self.network.snapshot(),
            "limits": self.limits.snapshot(),
            "storage": self.storage.snapshot(),
            "last_run": self._last_run,
        }


__all__ = ["Sandbox", "SandboxFn"]
