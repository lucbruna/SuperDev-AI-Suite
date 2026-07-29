from __future__ import annotations

import os
import signal
import threading
import time
from contextlib import contextmanager
from typing import Any, Callable

from .filesystem_policy import FileSystemPolicy
from .network_policy import NetworkPolicy
from .resource_limits import SandboxResourceLimits


class PermissionDeniedError(Exception):
    pass


class PluginSandbox:
    def __init__(
        self,
        filesystem_policy: FileSystemPolicy | None = None,
        network_policy: NetworkPolicy | None = None,
        resource_limits: SandboxResourceLimits | None = None,
    ) -> None:
        self._filesystem_policy = filesystem_policy or FileSystemPolicy()
        self._network_policy = network_policy or NetworkPolicy()
        self._resource_limits = resource_limits or SandboxResourceLimits()
        self._permission_checks: dict[str, list[str]] = {}

    def execute_safe(
        self,
        plugin_name: str,
        func_name: str,
        params: dict[str, Any] | None = None,
    ) -> Any:
        if params is None:
            params = {}

        import importlib
        import sys

        module_name = f"plugin_{plugin_name}"
        if module_name not in sys.modules:
            raise ImportError(f"Plugin '{plugin_name}' is not loaded")

        module = sys.modules[module_name]
        if not hasattr(module, func_name):
            raise AttributeError(f"Function '{func_name}' not found in plugin '{plugin_name}'")

        func = getattr(module, func_name)
        if not callable(func):
            raise TypeError(f"'{func_name}' is not callable in plugin '{plugin_name}'")

        permissions = self._permission_checks.get(plugin_name, [])
        if "execution" not in permissions:
            self._check_permissions(plugin_name, "execution")

        with self._resource_limits.apply():
            try:
                if params:
                    result = func(**params)
                else:
                    result = func()
            except PermissionError as e:
                raise PermissionDeniedError(str(e))

        return result

    def _check_permissions(self, plugin_name: str, permission: str) -> None:
        self._permission_checks.setdefault(plugin_name, []).append(permission)

    def check_filesystem(self, path: str, operation: str = "read") -> None:
        self._filesystem_policy.check(path, operation)

    def check_network(self, url: str) -> None:
        self._network_policy.check(url)