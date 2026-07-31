"""OpenTelemetry configuration for distributed tracing and metrics.

Configures OTLP exporters for traces and metrics. Gracefully degrades
if opentelemetry packages are not installed.
"""
from __future__ import annotations

import logging
import os

logger = logging.getLogger("superdev.telemetry")

# Feature flag — disable in testing
_enabled = os.getenv("OTEL_ENABLED", "true").lower() == "true"
_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318")
_service_name = os.getenv("OTEL_SERVICE_NAME", "superdev")
_environment = os.getenv("ENVIRONMENT", "development")


def configure_telemetry() -> None:
    """Set up OpenTelemetry tracing and metrics with OTLP exporters.

    Call once at application startup.  If the opentelemetry packages are
    missing, logs a warning and returns — the rest of the application
    continues to work without telemetry.
    """
    if not _enabled:
        logger.info("OpenTelemetry disabled via OTEL_ENABLED=false")
        return

    try:
        from opentelemetry import trace
        from opentelemetry.sdk.resources import SERVICE_NAME, Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        resource = Resource.create({
            SERVICE_NAME: _service_name,
            "deployment.environment": _environment,
        })

        provider = TracerProvider(resource=resource)

        try:
            from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
            exporter = OTLPSpanExporter(endpoint=_endpoint, insecure=True)
            provider.add_span_processor(BatchSpanProcessor(exporter))
            logger.info("OTLP trace exporter configured → %s", _endpoint)
        except Exception as e:
            logger.warning("OTLP trace exporter not available: %s", e)

        trace.set_tracer_provider(provider)
        logger.info("OpenTelemetry tracing configured (service=%s)", _service_name)

    except ImportError:
        logger.warning(
            "opentelemetry packages not installed — tracing disabled. "
            "Install with: pip install opentelemetry-api opentelemetry-sdk "
            "opentelemetry-exporter-otlp-proto-grpc"
        )
    except Exception as e:
        logger.error("Failed to configure OpenTelemetry: %s", e)


def get_tracer(name: str = "superdev"):
    """Get a tracer instance. Returns a no-op tracer if OTEL is unavailable."""
    try:
        from opentelemetry import trace
        return trace.get_tracer(name)
    except Exception:
        from opentelemetry.trace import NoOpTracer
        return NoOpTracer()
