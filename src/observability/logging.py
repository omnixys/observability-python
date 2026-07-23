from __future__ import annotations

import logging
import os
import re
from typing import TYPE_CHECKING, Any

import structlog
from opentelemetry._logs import set_logger_provider
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource

from observability.request_context import current_request_context

if TYPE_CHECKING:
    from collections.abc import MutableMapping

_SENSITIVE_KEY = re.compile(r"authorization|cookie|password|secret|token|api[-_]?key", re.IGNORECASE)


def _add_context(_logger: Any, _method_name: str, event_dict: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
    if _service_name:
        event_dict["service"] = _service_name
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


def _redact_sensitive(
    _logger: Any, _method_name: str, event_dict: MutableMapping[str, Any]
) -> MutableMapping[str, Any]:
    return _redact_mapping(event_dict)


def _redact_mapping(value: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
    for key, nested in tuple(value.items()):
        if _SENSITIVE_KEY.search(key):
            value[key] = "[REDACTED]"
        elif isinstance(nested, dict):
            value[key] = _redact_mapping(nested)
        elif isinstance(nested, list):
            value[key] = [
                _redact_mapping(item) if isinstance(item, dict) else item for item in nested
            ]
    return value


_logger_provider: LoggerProvider | None = None
_service_name: str | None = None


def _signal_endpoint(endpoint: str, signal: str) -> str:
    base = endpoint.rstrip("/")
    for suffix in ("/v1/traces", "/v1/logs"):
        if base.endswith(suffix):
            base = base[: -len(suffix)]
            break
    return f"{base}/v1/{signal}"


def _setup_otel_logging(service_name: str, endpoint: str, environment: str) -> LoggerProvider:
    global _logger_provider, _service_name
    resource = Resource.create(
        {
            "service.name": service_name,
            "service.namespace": "omnixys",
            "service.version": os.environ.get("OTEL_SERVICE_VERSION", "unknown"),
            "deployment.environment.name": environment,
        }
    )

    logger_provider = LoggerProvider(resource=resource)
    logger_provider.add_log_record_processor(
        BatchLogRecordProcessor(OTLPLogExporter(endpoint=_signal_endpoint(endpoint, "logs")))
    )
    set_logger_provider(logger_provider)

    handler = LoggingHandler(logger_provider=logger_provider)
    handler.setLevel(logging.DEBUG)
    logging.getLogger().addHandler(handler)
    _logger_provider = logger_provider
    _service_name = service_name
    return logger_provider


def configure_logging(
    log_level: str = "INFO",
    service_name: str | None = None,
    *,
    otlp_endpoint: str | None = None,
    environment: str = "local",
) -> None:
    if service_name:
        endpoint = otlp_endpoint or os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318")
        _setup_otel_logging(service_name, endpoint, environment)

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_log_level,
            _add_context,
            _redact_sensitive,
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


def shutdown_logging() -> None:
    global _logger_provider
    if _logger_provider is not None:
        _logger_provider.shutdown()
        _logger_provider = None
