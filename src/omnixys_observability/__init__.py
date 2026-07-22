from omnixys_observability.logging import configure_logging, get_logger
from omnixys_observability.metrics import (
    ObservabilityMetrics,
    ObservabilityMiddleware,
    auth_failures,
    cache_hits,
    cache_misses,
    db_query_duration,
    graphql_operations,
    http_request_duration,
    http_requests_total,
    kafka_publish_failures,
    kafka_publish_total,
    outbox_failed,
    outbox_pending,
    outbox_processed,
    outbox_processing_duration,
    rate_limit_blocked,
)
from omnixys_observability.request_context import (
    RequestContext,
    current_request_context,
    reset_request_context,
    set_request_context,
)
from omnixys_observability.tracing import configure_tracing, instrument_fastapi, shutdown_tracing, uninstrument_fastapi

__version__ = "1.1.0"

__all__ = [
    "ObservabilityMetrics",
    "ObservabilityMiddleware",
    "RequestContext",
    "auth_failures",
    "cache_hits",
    "cache_misses",
    "configure_logging",
    "configure_tracing",
    "current_request_context",
    "db_query_duration",
    "get_logger",
    "graphql_operations",
    "http_request_duration",
    "http_requests_total",
    "instrument_fastapi",
    "kafka_publish_failures",
    "kafka_publish_total",
    "outbox_failed",
    "outbox_pending",
    "outbox_processed",
    "outbox_processing_duration",
    "rate_limit_blocked",
    "reset_request_context",
    "set_request_context",
    "shutdown_tracing",
    "uninstrument_fastapi",
]
