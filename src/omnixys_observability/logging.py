from __future__ import annotations

from typing import TYPE_CHECKING, Any

import structlog
from opentelemetry import trace

from omnixys_observability.request_context import current_request_context

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
        event_dict["trace_id"] = hex(span_context.trace_id)
        event_dict["span_id"] = hex(span_context.span_id)

    return event_dict


def configure_logging(_level: str = "INFO") -> None:
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


def get_logger(name: str | None = None) -> Any:
    return structlog.get_logger(name)
