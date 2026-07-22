from __future__ import annotations

from contextvars import ContextVar
from dataclasses import dataclass, field


@dataclass
class RequestContext:
    user_id: str | None = None
    organization_id: str | None = None
    roles: list[str] = field(default_factory=list)
    scope: list[str] = field(default_factory=list)
    correlation_id: str | None = None
    request_id: str | None = None
    trace_id: str | None = None
    span_id: str | None = None
    is_authenticated: bool = False


_request_context_var: ContextVar[RequestContext | None] = ContextVar("observability_request_context", default=None)


def current_request_context() -> RequestContext | None:
    return _request_context_var.get()


def set_request_context(ctx: RequestContext) -> None:
    _request_context_var.set(ctx)


def reset_request_context() -> None:
    _request_context_var.set(None)
