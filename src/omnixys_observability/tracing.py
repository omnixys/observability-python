from __future__ import annotations

from typing import Any, cast

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


def configure_tracing(
    service_name: str = "omnixys",
    otlp_endpoint: str = "http://localhost:4318/v1/traces",
    environment: str = "local",
    _sampling_probability: float = 0.1,
) -> None:
    resource = Resource.create({
        "service.name": service_name,
        "deployment.environment": environment,
    })
    provider = TracerProvider(resource=resource)
    exporter = OTLPSpanExporter(endpoint=otlp_endpoint)
    processor = BatchSpanProcessor(exporter)
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)
    LoggingInstrumentor().instrument()
    HTTPXClientInstrumentor().instrument()


def instrument_fastapi(app: Any) -> None:
    FastAPIInstrumentor.instrument_app(app)


def uninstrument_fastapi(app: Any) -> None:
    FastAPIInstrumentor.uninstrument_app(app)


def shutdown_tracing() -> None:
    provider = cast("TracerProvider", trace.get_tracer_provider())
    provider.shutdown()
