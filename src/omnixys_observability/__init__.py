from omnixys_observability.logging import configure_logging, get_logger
from omnixys_observability.metrics import (
    ObservabilityMetrics,
    auth_failures,
    cache_hits,
    cache_misses,
    db_query_duration,
    graphql_operations,
    http_request_duration,
    http_requests_total,
    kafka_publish_failures,
    kafka_publish_total,
    rate_limit_blocked,
)
from omnixys_observability.tracing import configure_tracing, instrument_fastapi, shutdown_tracing, uninstrument_fastapi

__version__ = "1.0.0"

__all__ = [
    "ObservabilityMetrics",
    "auth_failures",
    "cache_hits",
    "cache_misses",
    "configure_logging",
    "configure_tracing",
    "db_query_duration",
    "get_logger",
    "graphql_operations",
    "http_request_duration",
    "http_requests_total",
    "kafka_publish_failures",
    "kafka_publish_total",
    "rate_limit_blocked",
    "instrument_fastapi",
    "shutdown_tracing",
    "uninstrument_fastapi",
]
