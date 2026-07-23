from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING, Any

import structlog
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.sdk._logs import BatchLogRecordProcessor, LoggerProvider, LoggingHandler
from opentelemetry.sdk.resources import Resource

from observability.request_context import current_request_context

if TYPE_CHECKING:
    from collections.abc import MutableMapping


def _add_context(_logger: Any, _method_name: str, event_dict: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
    ctx = current_request_context()
    if ctx:
        if ctx.correlation_id:
            event_dict["correlation_id"] = ctx.correlation_id
        if ctx.user_id:
            event_dict["user_id"] = ctx.user_id
        if ctx.organization_id:
            event_dict["organization_id"] = ctx.organization_id

    span = trace.get_current_span()
    span_context = span.get_span_context()
    if span_context.is_valid:
        event_dict["traceId"] = format(span_context.trace_id, "032x")
        event_dict["spanId"] = format(span_context.span_id, "016x")

    return event_dict


def _setup_otel_logging(service_name: str) -> None:
    endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318")
    resource = Resource.create(
        {
            "service.name": service_name,
            "service.namespace": "omnixys",
        }
    )

    logger_provider = LoggerProvider(resource=resource)
    logger_provider.add_log_record_processor(
        BatchLogRecordProcessor(OTLPLogExporter(endpoint=f"{endpoint}/v1/logs"))
    )

    handler = LoggingHandler(logger_provider=logger_provider)
    handler.setLevel(logging.DEBUG)
    logging.getLogger().addHandler(handler)


def configure_logging(log_level: str = "INFO", service_name: str | None = None) -> None:
    if service_name:
        _setup_otel_logging(service_name)

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_log_level,
            _add_context,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format="%(message)s",
    )


def get_logger(name: str | None = None) -> Any:
    return structlog.get_logger(name)
