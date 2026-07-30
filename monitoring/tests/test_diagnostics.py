from __future__ import annotations

import pytest

from SuperDev.monitoring.diagnostics.diagnostic_engine import DiagnosticEngine
from SuperDev.monitoring.diagnostics.system_diagnostics import SystemDiagnostics
from SuperDev.monitoring.diagnostics.network_diagnostics import NetworkDiagnostics
from SuperDev.monitoring.diagnostics.configuration_check import ConfigurationCheck
from SuperDev.monitoring.diagnostics.connectivity_check import ConnectivityCheck


class TestDiagnosticEngine:
    def test_run_check(self) -> None:
        engine = DiagnosticEngine()
        engine.register_check("test", lambda: {"status": "ok"})
        result = engine.run_check("test")
        assert result is not None


class TestSystemDiagnostics:
    def test_collect(self) -> None:
        diag = SystemDiagnostics()
        data = diag.collect()
        assert "platform" in data


class TestNetworkDiagnostics:
    def test_localhost(self) -> None:
        diag = NetworkDiagnostics()
        result = diag.check_localhost()
        assert result is not None


class TestConfigurationCheck:
    def test_check_env(self) -> None:
        check = ConfigurationCheck()
        result = check.check_env("PATH")
        assert result.passed is True


class TestConnectivityCheck:
    def test_check_url(self) -> None:
        check = ConnectivityCheck()
        result = check.check_url("http://localhost:9999", timeout=1)
        assert result.passed is False
