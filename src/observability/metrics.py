from __future__ import annotations

from time import time
from typing import TYPE_CHECKING, Any

from prometheus_client import Counter, Gauge, Histogram

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

SERVICE_PREFIX = "omnixys"

http_requests_total = Counter(
    f"{SERVICE_PREFIX}_http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status_code"],
)

http_request_duration = Histogram(
    f"{SERVICE_PREFIX}_http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "path"],
)

graphql_operations = Counter(
    f"{SERVICE_PREFIX}_graphql_operations_total",
    "Total GraphQL operations",
    ["operation_type", "operation_name"],
)

db_query_duration = Histogram(
    f"{SERVICE_PREFIX}_db_query_duration_seconds",
    "Database query duration in seconds",
    ["statement"],
)

kafka_publish_total = Counter(
    f"{SERVICE_PREFIX}_kafka_publish_total",
    "Total Kafka messages published",
    ["topic", "event_type"],
)

kafka_publish_failures = Counter(
    f"{SERVICE_PREFIX}_kafka_publish_failures_total",
    "Total Kafka publish failures",
    ["topic", "event_type"],
)

cache_hits = Counter(
    f"{SERVICE_PREFIX}_cache_hits_total",
    "Total cache hits",
)

cache_misses = Counter(
    f"{SERVICE_PREFIX}_cache_misses_total",
    "Total cache misses",
)

rate_limit_blocked = Counter(
    f"{SERVICE_PREFIX}_rate_limit_blocked_total",
    "Total requests blocked by rate limiter",
)

auth_failures = Counter(
    f"{SERVICE_PREFIX}_auth_failures_total",
    "Total authentication failures",
)

outbox_pending = Gauge(
    f"{SERVICE_PREFIX}_outbox_pending_total",
    "Current number of pending outbox messages",
)

outbox_processed = Counter(
    f"{SERVICE_PREFIX}_outbox_messages_processed_total",
    "Total outbox messages processed",
    ["event_type"],
)

outbox_failed = Counter(
    f"{SERVICE_PREFIX}_outbox_messages_failed_total",
    "Total outbox messages failed",
    ["event_type"],
)

outbox_processing_duration = Histogram(
    f"{SERVICE_PREFIX}_outbox_processing_duration_seconds",
    "Outbox processing duration in seconds",
    ["event_type"],
)


class ObservabilityMetrics:
    def __init__(self) -> None:
        self.http_requests_total = http_requests_total
        self.http_request_duration = http_request_duration
        self.graphql_operations = graphql_operations
        self.db_query_duration = db_query_duration
        self.kafka_publish_total = kafka_publish_total
        self.kafka_publish_failures = kafka_publish_failures
        self.cache_hits = cache_hits
        self.cache_misses = cache_misses
        self.rate_limit_blocked = rate_limit_blocked
        self.auth_failures = auth_failures
        self.outbox_pending = outbox_pending
        self.outbox_processed = outbox_processed
        self.outbox_failed = outbox_failed
        self.outbox_processing_duration = outbox_processing_duration


class ObservabilityMiddleware:
    def __init__(
        self,
        app: Callable[..., Awaitable[Any]],
    ) -> None:
        self.app = app

    async def __call__(
        self,
        scope: dict[str, Any],
        receive: Callable[[], Awaitable[Any]],
        send: Callable[[dict[str, Any]], Awaitable[None]],
    ) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        method = scope.get("method", "UNKNOWN")
        path = scope.get("path", "/")
        start = time()

        status_code = [200]

        async def _send_wrapper(message: dict[str, Any]) -> None:
            if message["type"] == "http.response.start":
                status_code[0] = message.get("status", 200)
            await send(message)

        try:
            await self.app(scope, receive, _send_wrapper)
        finally:
            duration = time() - start
            http_requests_total.labels(method=method, path=path, status_code=str(status_code[0])).inc()
            http_request_duration.labels(method=method, path=path).observe(duration)
