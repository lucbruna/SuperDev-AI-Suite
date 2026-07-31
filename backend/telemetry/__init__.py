from __future__ import annotations

import logging
from typing import Any

from backend.telemetry.telemetry_manager import TelemetryManager, telemetry_manager

logger = logging.getLogger("superdev")


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

        resource = Resource.create({"service.name": settings.service_name})
        provider = TracerProvider(resource=resource)
        exporter = OTLPSpanExporter(endpoint=settings.exporter_endpoint, headers=getattr(settings, "headers", None))
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

        resource = Resource.create({"service.name": settings.service_name})
        reader = PeriodicExportingMetricReader(
            OTLPMetricExporter(endpoint=settings.exporter_endpoint, headers=getattr(settings, "headers", None))
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
