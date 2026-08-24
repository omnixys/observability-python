from __future__ import annotations

import json
import logging
import os
import re
import sys
from typing import TYPE_CHECKING, Any, TextIO

import structlog
from opentelemetry import trace
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource
from structlog.dev import ConsoleRenderer

from observability.request_context import current_request_context

if TYPE_CHECKING:
    from collections.abc import MutableMapping

_SENSITIVE_KEY = re.compile(r"authorization|cookie|password|secret|token|api[-_]?key", re.IGNORECASE)


def _add_context(_logger: Any, _method_name: str, event_dict: MutableMapping[str, Any]) -> MutableMapping[str, Any]:  # noqa: C901
    if _service_name:
        event_dict["service"] = _service_name
    ctx = current_request_context()
    if ctx:
        if ctx.request_id:
            event_dict["request_id"] = ctx.request_id
        if ctx.correlation_id:
            event_dict["correlation_id"] = ctx.correlation_id
        if ctx.user_id:
            event_dict["user_id"] = ctx.user_id
            event_dict["actor_id"] = ctx.user_id
        if ctx.tenant_id:
            event_dict["tenant_id"] = ctx.tenant_id

    span = trace.get_current_span()
    span_context = span.get_span_context()
    if span_context.is_valid:
        event_dict["traceId"] = format(span_context.trace_id, "032x")
        event_dict["spanId"] = format(span_context.span_id, "016x")
    elif ctx:
        if ctx.trace_id:
            event_dict["traceId"] = ctx.trace_id
        if ctx.span_id:
            event_dict["spanId"] = ctx.span_id

    return event_dict


def _redact_sensitive(
    _logger: Any,
    _method_name: str,
    event_dict: MutableMapping[str, Any],
) -> MutableMapping[str, Any]:
    return _redact_mapping(event_dict)


def _redact_mapping(value: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
    for key, nested in tuple(value.items()):
        if _SENSITIVE_KEY.search(key):
            value[key] = "[REDACTED]"
        elif isinstance(nested, dict):
            value[key] = _redact_mapping(nested)
        elif isinstance(nested, list):
            value[key] = [_redact_mapping(item) if isinstance(item, dict) else item for item in nested]
    return value


_logger_provider: LoggerProvider | None = None
_service_name: str | None = None
_console_handlers: list[logging.Handler] = []
_otlp_handler: logging.Handler | None = None
_otel_logger_provider_registered = False


def _signal_endpoint(endpoint: str, signal: str) -> str:
    base = endpoint.rstrip("/")
    for suffix in ("/v1/traces", "/v1/logs"):
        if base.endswith(suffix):
            base = base[: -len(suffix)]
            break
    return f"{base}/v1/{signal}"


def _resolve_level(value: str | None, default: int) -> int:
    if not value:
        return default
    return getattr(logging, value.strip().upper(), default)


def _setup_otel_logging(service_name: str, endpoint: str, environment: str, level: int) -> LoggerProvider:
    global _logger_provider, _service_name, _otlp_handler, _otel_logger_provider_registered  # noqa: PLW0603
    if _logger_provider is not None:
        return _logger_provider
    resource = Resource.create(
        {
            "service.name": service_name,
            "service.namespace": "omnixys",
            "service.version": os.environ.get("OTEL_SERVICE_VERSION", "unknown"),
            "deployment.environment.name": environment,
        },
    )

    logger_provider = LoggerProvider(resource=resource)
    logger_provider.add_log_record_processor(
        BatchLogRecordProcessor(OTLPLogExporter(endpoint=_signal_endpoint(endpoint, "logs"))),
    )
    if not _otel_logger_provider_registered:
        set_logger_provider(logger_provider)
        _otel_logger_provider_registered = True

    root = logging.getLogger()
    if _otlp_handler is not None:
        root.removeHandler(_otlp_handler)
    handler = LoggingHandler(logger_provider=logger_provider)
    handler.setLevel(level)
    root.addHandler(handler)
    _otlp_handler = handler
    _logger_provider = logger_provider
    _service_name = service_name
    return logger_provider


def _console_pretty(environment: str) -> bool:
    flag = os.environ.get("LOG_PRETTY")
    if flag == "true":
        return True
    if flag == "false":
        return False
    return environment.lower() != "production"


class _JsonConsoleFormatter(logging.Formatter):
    """Re-render structlog JSON messages as readable colored console lines."""

    def __init__(self, *, colors: bool) -> None:
        super().__init__(fmt="%(message)s")
        self._renderer = ConsoleRenderer(colors=colors)

    def format(self, record: logging.LogRecord) -> str:
        message = record.getMessage()
        try:
            event_dict = json.loads(message)
        except TypeError, ValueError:
            return message
        if not isinstance(event_dict, dict):
            return message
        event_dict.pop("level_number", None)
        return self._renderer(None, None, event_dict)  # type: ignore[arg-type]


def _build_console_formatter(*, pretty: bool) -> logging.Formatter:
    if pretty:
        return _JsonConsoleFormatter(colors=True)
    return logging.Formatter("%(message)s")


def configure_logging(  # noqa: PLR0913
    log_level: str = "INFO",
    service_name: str | None = None,
    *,
    otlp_endpoint: str | None = None,
    environment: str = "local",
    console_stream: TextIO | None = None,
    otel_log_level: str | None = None,
) -> None:
    """Configure console and OTLP logging with independent thresholds.

    The root logger is lowered to the least verbose of both levels so DEBUG
    records can reach the OTLP handler (and therefore Loki) even while the
    console handler stays on ``INFO`` in production. The OTLP threshold is
    controlled via ``otel_log_level`` or the ``OTEL_LOG_LEVEL`` environment
    variable and defaults to ``DEBUG``.
    """
    level = _resolve_level(log_level, logging.INFO)
    otel_level = _resolve_level(
        otel_log_level if otel_log_level is not None else os.environ.get("OTEL_LOG_LEVEL"),
        logging.DEBUG,
    )
    root = logging.getLogger()
    root.setLevel(min(level, otel_level))

    for handler in _console_handlers:
        root.removeHandler(handler)
    _console_handlers.clear()

    stream = console_stream if console_stream is not None else sys.stdout
    console_handler = logging.StreamHandler(stream)
    console_handler.setLevel(level)
    console_handler.setFormatter(_build_console_formatter(pretty=_console_pretty(environment)))
    root.addHandler(console_handler)
    _console_handlers.append(console_handler)

    if service_name:
        endpoint = otlp_endpoint or os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318")
        _setup_otel_logging(service_name, endpoint, environment, level=otel_level)

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_log_level,
            _add_context,
            _redact_sensitive,
            structlog.processors.format_exc_info,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str | None = None) -> Any:
    return structlog.get_logger(name)


def shutdown_logging() -> None:
    global _logger_provider, _otlp_handler  # noqa: PLW0603
    root = logging.getLogger()
    if _otlp_handler is not None:
        root.removeHandler(_otlp_handler)
        _otlp_handler = None
    if _logger_provider is not None:
        _logger_provider.shutdown()
        _logger_provider = None
