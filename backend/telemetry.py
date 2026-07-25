from __future__ import annotations

import logging
from typing import Any

from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from backend.config import config
from backend.settings import TelemetrySettings

logger = logging.getLogger("superdev")


def configure_tracing(settings: TelemetrySettings | None = None) -> TracerProvider | None:
    if not settings:
        settings = config.telemetry
    if not settings.enabled or not settings.traces_enabled:
        logger.info("Tracing is disabled")
        return None

    resource = Resource.create({"service.name": settings.service_name})
    provider = TracerProvider(resource=resource)
    exporter = OTLPSpanExporter(endpoint=settings.otlp_endpoint, headers=settings.headers)
    processor = BatchSpanProcessor(exporter)
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)
    logger.info("Tracing configured with OTLP endpoint", extra={"endpoint": settings.otlp_endpoint})
    return provider


def configure_metrics(settings: TelemetrySettings | None = None) -> MeterProvider | None:
    if not settings:
        settings = config.telemetry
    if not settings.enabled or not settings.metrics_enabled:
        logger.info("Metrics are disabled")
        return None

    resource = Resource.create({"service.name": settings.service_name})
    reader = PeriodicExportingMetricReader(
        OTLPMetricExporter(endpoint=settings.otlp_endpoint, headers=settings.headers)
    )
    provider = MeterProvider(resource=resource, metric_readers=[reader])
    metrics.set_meter_provider(provider)
    logger.info("Metrics configured with OTLP endpoint", extra={"endpoint": settings.otlp_endpoint})
    return provider


def instrument_fastapi(app: Any) -> None:
    FastAPIInstrumentor.instrument_app(app)