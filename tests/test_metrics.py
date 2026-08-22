"""Behavioral tests for rate-limit and SLO metrics."""

from __future__ import annotations

import asyncio

from observability import RateLimitMetrics, SloMetrics


def test_rate_limit_metrics_counts_per_key() -> None:
    metrics = RateLimitMetrics()
    metrics.hit("sms:user:42")
    metrics.hit("sms:user:42")
    metrics.hit("sms:user:7")

    assert metrics.get("sms:user:42") == 2
    assert metrics.get("sms:user:7") == 1
    assert metrics.get("missing") == 0


def test_rate_limit_metrics_reset() -> None:
    metrics = RateLimitMetrics()
    metrics.hit("a")
    metrics.hit("b")
    metrics.reset("a")
    assert metrics.get("a") == 0
    assert metrics.get("b") == 1

    metrics.reset()
    assert metrics.totals() == {}


def test_slo_metrics_error_rate() -> None:
    slo = SloMetrics()
    assert slo.error_rate() == 0.0

    slo.record_success()
    slo.record_success()
    slo.record_error()
    slo.record_error()

    assert slo.total == 4
    assert slo.errors == 2
    assert slo.error_rate() == 0.5


def test_metrics_middleware_records_http_totals() -> None:
    from observability import ObservabilityMiddleware, http_request_duration, http_requests_total

    received: list[dict] = []

    async def app(scope, receive, send) -> None:
        response_start = {
            "type": "http.response.start",
            "status": 201,
        }
        await send(response_start)
        received.append(scope)

    async def _noop_receive() -> None:
        return None

    async def _noop_send(_message: dict) -> None:
        return None

    middleware = ObservabilityMiddleware(app)
    asyncio.run(
        middleware(
            {"type": "http", "method": "POST", "path": "/events"},
            _noop_receive,
            _noop_send,
        ),
    )

    assert len(received) == 1
    sample = http_requests_total.labels(method="POST", path="/events", status_code="201")
    assert sample._value.get() > 0
    duration_samples = http_request_duration.labels(method="POST", path="/events")._sum.get()
    assert duration_samples > 0


def test_metrics_middleware_passes_through_non_http() -> None:
    from observability import ObservabilityMiddleware

    calls: list[str] = []

    async def app(scope, receive, send) -> None:
        calls.append(scope["type"])

    middleware = ObservabilityMiddleware(app)
    asyncio.run(middleware({"type": "lifespan"}, None, None))

    assert calls == ["lifespan"]
