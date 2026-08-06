from __future__ import annotations

import logging
import socket
from typing import Any
from urllib.parse import urlparse

from backend.telemetry.telemetry_manager import TelemetryManager, telemetry_manager

logger = logging.getLogger("superdev")


def _endpoint_reachable(endpoint: str, timeout: float = 1.0) -> bool:
    """Return True if an OTLP collector answers at ``endpoint``.

    Probes the host:port with a short TCP connect. Keeps the app from
    creating OTLP exporters (and their endless retry/backoff log spam)
    when no collector is actually running.
    """
    try:
        parsed = urlparse(endpoint)
        host = parsed.hostname or "localhost"
        port = parsed.port or 4318
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def configure_tracing(settings=None):
    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        if not settings:
            from backend.config import config

            settings = config.telemetry
        if not settings.enabled or not settings.traces_enabled:
            logger.info("Tracing is disabled")
            return None

        endpoint = getattr(settings, "traces_endpoint", "") or settings.exporter_endpoint
        if not _endpoint_reachable(endpoint):
            logger.warning(
                "OTLP collector not reachable at %s — OTLP trace export disabled", endpoint
            )
            return None

        resource = Resource.create({"service.name": settings.service_name})
        provider = TracerProvider(resource=resource)
        exporter = OTLPSpanExporter(endpoint=endpoint, headers=getattr(settings, "headers", None))
        processor = BatchSpanProcessor(exporter)
        provider.add_span_processor(processor)
        trace.set_tracer_provider(provider)
        return provider
    except ImportError:
        logger.info("OpenTelemetry not installed, tracing disabled")
        return None


def configure_metrics(settings=None):
    try:
        from opentelemetry import metrics
        from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
        from opentelemetry.sdk.metrics import MeterProvider
        from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
        from opentelemetry.sdk.resources import Resource

        if not settings:
            from backend.config import config

            settings = config.telemetry
        if not settings.enabled or not settings.metrics_enabled:
            logger.info("Metrics are disabled")
            return None

        endpoint = getattr(settings, "metrics_endpoint", "") or settings.exporter_endpoint
        if not _endpoint_reachable(endpoint):
            logger.warning(
                "OTLP collector not reachable at %s — OTLP metrics export disabled", endpoint
            )
            return None

        resource = Resource.create({"service.name": settings.service_name})
        reader = PeriodicExportingMetricReader(
            OTLPMetricExporter(endpoint=endpoint, headers=getattr(settings, "headers", None))
        )
        provider = MeterProvider(resource=resource, metric_readers=[reader])
        metrics.set_meter_provider(provider)
        return provider
    except ImportError:
        logger.info("OpenTelemetry not installed, metrics disabled")
        return None


def instrument_fastapi(app: Any) -> None:
    try:
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

        FastAPIInstrumentor.instrument_app(app)
    except ImportError:
        pass


__all__ = [
    "TelemetryManager",
    "telemetry_manager",
    "configure_tracing",
    "configure_metrics",
    "instrument_fastapi",
]
