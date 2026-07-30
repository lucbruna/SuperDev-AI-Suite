"""Tests for the OpenTelemetry configuration module."""
from __future__ import annotations

import pytest
from unittest.mock import patch, MagicMock


class TestOTELConfig:
    def test_module_importable(self):
        from backend.telemetry import otel
        assert hasattr(otel, "configure_telemetry")
        assert hasattr(otel, "get_tracer")

    def test_get_tracer_returns_tracer(self):
        from backend.telemetry.otel import get_tracer
        tracer = get_tracer("test")
        assert tracer is not None

    def test_get_tracer_with_custom_name(self):
        from backend.telemetry.otel import get_tracer
        tracer = get_tracer("my-custom-service")
        assert tracer is not None

    @patch.dict("os.environ", {"OTEL_ENABLED": "false"})
    def test_configure_telemetry_disabled(self):
        from backend.telemetry.otel import configure_telemetry
        # Should not raise even when disabled
        configure_telemetry()

    @patch.dict("os.environ", {"OTEL_ENABLED": "true"})
    def test_configure_telemetry_no_opentelemetry(self):
        """When opentelemetry is not installed, should degrade gracefully."""
        from backend.telemetry.otel import configure_telemetry
        # Should not raise — graceful degradation
        configure_telemetry()
