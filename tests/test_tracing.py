"""Behavioral tests for the span decorator and request context."""

from __future__ import annotations

from opentelemetry import trace

from observability import (
    RequestContext,
    current_request_context,
    reset_request_context,
    set_request_context,
    span,
)


@span
def sync_add(a: int, b: int) -> int:
    return a + b


@span(name="custom.compute", attributes={"source": "tests"})
async def async_compute() -> str:
    return "done"


def test_span_decorator_keeps_result() -> None:
    assert sync_add(2, 3) == 5


def test_span_decorator_async_keeps_result() -> None:
    import asyncio

    assert asyncio.run(async_compute()) == "done"


def test_span_decorator_propagates_errors() -> None:
    import asyncio

    @span
    async def broken() -> None:
        raise ValueError("nope")

    try:
        asyncio.run(broken())
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError to propagate")


def test_span_records_attributes() -> None:
    import asyncio

    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor
    from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    trace.set_tracer_provider(provider)

    @span(name="custom.compute", attributes={"source": "tests"})
    async def compute() -> str:
        return "done"

    assert asyncio.run(compute()) == "done"
    spans = exporter.get_finished_spans()
    assert len(spans) == 1
    assert spans[0].name == "custom.compute"
    assert spans[0].attributes == {"source": "tests"}  # type: ignore[union-attr]


def test_request_context_roundtrip() -> None:
    reset_request_context()
    assert current_request_context() is None

    ctx = RequestContext(request_id="r1", user_id="u1", tenant_id="t1")
    set_request_context(ctx)
    assert current_request_context() is ctx
    assert ctx.request_id == "r1"

    reset_request_context()
    assert current_request_context() is None


def test_request_context_defaults() -> None:
    ctx = RequestContext()
    assert ctx.is_authenticated is False
    assert ctx.roles == []
    assert ctx.scope == []
