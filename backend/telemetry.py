"""Telemetry configuration for OpenTelemetry tracing, metrics, and FastAPI instrumentation.

All opentelemetry imports are wrapped in try/except so the app starts gracefully
when optional dependencies are not installed.
"""

from __future__ import annotations

import logging
from typing import Any

from backend.config import config
from backend.settings import TelemetrySettings

logger = logging.getLogger("superdev")

# ─── Optional OpenTelemetry imports ──────────────────────────────────────────

try:
    from opentelemetry import metrics, trace
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.sdk.resources import Resource

    _HAS_OTEL = True
except ImportError:
    metrics = None  # type: ignore[assignment]
    trace = None  # type: ignore[assignment]
    FastAPIInstrumentor = None  # type: ignore[assignment]
    Resource = None  # type: ignore[assignment]
    _HAS_OTEL = False
    logger.info("OpenTelemetry SDK not installed — telemetry disabled")

try:
    from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    _HAS_OTLP = True
except ImportError:
    OTLPMetricExporter = None  # type: ignore[assignment]
    OTLPSpanExporter = None  # type: ignore[assignment]
    MeterProvider = None  # type: ignore[assignment]
    PeriodicExportingMetricReader = None  # type: ignore[assignment]
    TracerProvider = None  # type: ignore[assignment]
    BatchSpanProcessor = None  # type: ignore[assignment]
    _HAS_OTLP = False
    logger.info("OpenTelemetry OTLP exporter not installed — OTLP export disabled")


# ─── Helpers ──────────────────────────────────────────────────────────────────


def _otel_setting(settings: TelemetrySettings, name: str, default: str = "") -> str:
    """Safely access a TelemetrySettings attribute, returning a default if missing."""
    return str(getattr(settings, name, default))


# ─── Configuration ────────────────────────────────────────────────────────────


def configure_tracing(settings: TelemetrySettings | None = None) -> Any | None:
    """Configure OpenTelemetry tracing.

    Returns None silently when opentelemetry is not installed or disabled.
    """
    if not _HAS_OTEL or not _HAS_OTLP:
        return None
    if not settings:
        settings = config.telemetry
    if not settings.enabled or not settings.traces_enabled:
        logger.info("Tracing is disabled")
        return None

    try:
        endpoint = _otel_setting(settings, "traces_endpoint") or _otel_setting(
            settings, "exporter_endpoint", "http://localhost:4318"
        )
        resource = Resource.create({"service.name": settings.service_name})
        provider = TracerProvider(resource=resource)
        exporter = OTLPSpanExporter(endpoint=endpoint)
        processor = BatchSpanProcessor(exporter)
        provider.add_span_processor(processor)
        trace.set_tracer_provider(provider)  # type: ignore[union-attr]
        logger.info("Tracing configured with endpoint: %s", endpoint)
        return provider
    except Exception as e:
        logger.warning("Failed to configure tracing: %s", e)
        return None


def configure_metrics(settings: TelemetrySettings | None = None) -> Any | None:
    """Configure OpenTelemetry metrics.

    Returns None silently when opentelemetry is not installed or disabled.
    """
    if not _HAS_OTEL or not _HAS_OTLP:
        return None
    if not settings:
        settings = config.telemetry
    if not settings.enabled or not settings.metrics_enabled:
        logger.info("Metrics are disabled")
        return None

    try:
        endpoint = _otel_setting(settings, "metrics_endpoint") or _otel_setting(
            settings, "exporter_endpoint", "http://localhost:4318"
        )
        resource = Resource.create({"service.name": settings.service_name})
        reader = PeriodicExportingMetricReader(
            OTLPMetricExporter(endpoint=endpoint),
        )
        provider = MeterProvider(resource=resource, metric_readers=[reader])
        metrics.set_meter_provider(provider)  # type: ignore[union-attr]
        logger.info("Metrics configured with endpoint: %s", endpoint)
        return provider
    except Exception as e:
        logger.warning("Failed to configure metrics: %s", e)
        return None


def instrument_fastapi(app: Any) -> None:
    """Instrument a FastAPI app with OpenTelemetry."""
    if not _HAS_OTEL or FastAPIInstrumentor is None:
        return
    try:
        FastAPIInstrumentor.instrument_app(app)
        logger.info("FastAPI instrumented with OpenTelemetry")
    except Exception as e:
        logger.warning("Failed to instrument FastAPI: %s", e)
