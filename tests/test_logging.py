"""Tests for observability.logging console rendering."""

from __future__ import annotations

import io
import logging
import os
import re
from typing import TYPE_CHECKING

import pytest
import structlog
from opentelemetry.sdk._logs import LoggingHandler

from observability import configure_logging, get_logger, shutdown_logging

if TYPE_CHECKING:
    from collections.abc import Iterator

_ANSI = re.compile(r"\x1b\[[0-9;]*m")

pytestmark = pytest.mark.filterwarnings(
    "ignore:`LoggingHandler` in `opentelemetry-sdk` is deprecated.*:DeprecationWarning",
)


def _reset_logging() -> None:
    shutdown_logging()
    root = logging.getLogger()
    for handler in list(root.handlers):
        root.removeHandler(handler)
    os.environ.pop("LOG_PRETTY", None)
    structlog.reset_defaults()


@pytest.fixture(autouse=True)
def _cleanup_logging(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    _reset_logging()
    monkeypatch.setattr("observability.logging.OTLPLogExporter", _FakeExporter)
    yield
    _reset_logging()


def _strip_ansi(text: str) -> str:
    return _ANSI.sub("", text)


def _capture(environment: str = "local") -> io.StringIO:
    buf = io.StringIO()
    configure_logging(
        "INFO",
        "test-service",
        environment=environment,
        console_stream=buf,
    )
    return buf


def test_pretty_console_renders_readable_colored_lines() -> None:
    buf = _capture(environment="local")
    get_logger("test").info("application_started", channel="WHATSAPP", provider="evolution")

    out = buf.getvalue()
    assert "\x1b[" in out, "pretty console output must be colored"
    plain = _strip_ansi(out)
    first_line = plain.splitlines()[0]
    assert first_line.startswith("20"), "timestamp must be the first column"
    assert "[info" in first_line, "level must be present"
    assert "application_started" in first_line, "event must be present"
    assert "channel=WHATSAPP" in first_line, "metadata must be key=value"
    assert "service=test-service" in first_line
    assert "{" not in first_line, "pretty console must not be raw JSON"


def test_warning_and_error_levels_are_visible() -> None:
    buf = _capture(environment="local")
    get_logger("test").warning("health_check_down", service="tempo")
    get_logger("test").error("kafka_setup_failed", broker="kafka:9092")

    plain = _strip_ansi(buf.getvalue())
    assert "[warning" in plain
    assert "[error" in plain
    assert "health_check_down" in plain
    assert "kafka_setup_failed" in plain


def _raise_boom() -> None:
    message = "boom"
    raise RuntimeError(message)


def test_exception_traceback_is_rendered() -> None:
    buf = _capture(environment="local")
    try:
        _raise_boom()
    except RuntimeError:
        get_logger("test").exception("job_failed")

    plain = _strip_ansi(buf.getvalue())
    assert "Traceback (most recent call last):" in plain
    assert "RuntimeError: boom" in plain


def test_production_defaults_to_json_console(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("LOG_PRETTY", raising=False)
    buf = _capture(environment="production")
    get_logger("test").info("started")

    line = buf.getvalue().strip().splitlines()[0]
    assert line.startswith("{"), "production console must stay JSON by default"
    assert '"event": "started"' in line


def test_log_pretty_true_overrides_production(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LOG_PRETTY", "true")
    buf = _capture(environment="production")
    get_logger("test").info("started")

    assert "\x1b[" in buf.getvalue(), "LOG_PRETTY=true must force pretty console"


def test_log_pretty_false_disables_colors(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LOG_PRETTY", "false")
    buf = _capture(environment="local")
    get_logger("test").info("started")

    assert "\x1b[" not in buf.getvalue()
    assert buf.getvalue().strip().startswith("{")


def test_plain_stdlib_messages_pass_through() -> None:
    buf = _capture(environment="local")
    logging.getLogger("uvicorn").warning("shutting down gracefully")

    plain = _strip_ansi(buf.getvalue())
    assert "shutting down gracefully" in plain


def test_redaction_still_applies() -> None:
    buf = _capture(environment="local")
    payload = "secret-value"
    get_logger("test").info("outbound", authorization="Bearer abc123", token=payload)

    plain = _strip_ansi(buf.getvalue())
    assert "Bearer abc123" not in plain
    assert "secret-value" not in plain
    assert "[REDACTED]" in plain


class _FakeExporter:
    def __init__(self, *_args: object, **_kwargs: object) -> None:
        pass

    def export(self, _batch: object) -> object:
        return None

    def shutdown(self) -> None:
        return None

    def force_flush(self, _timeout_millis: int = 30000) -> bool:
        return True


def test_otlp_handler_attached_when_service_name() -> None:
    buf = io.StringIO()
    configure_logging(
        "INFO",
        "test-service",
        environment="local",
        console_stream=buf,
    )

    handlers = logging.getLogger().handlers
    assert any(isinstance(h, LoggingHandler) for h in handlers)
    assert any(isinstance(h, logging.StreamHandler) for h in handlers)


def test_shutdown_logging_removes_otlp_handler() -> None:
    configure_logging("INFO", "test-service", environment="local", console_stream=io.StringIO())
    assert any(isinstance(h, LoggingHandler) for h in logging.getLogger().handlers)

    shutdown_logging()

    assert not any(isinstance(h, LoggingHandler) for h in logging.getLogger().handlers)


def test_reconfigure_after_shutdown_does_not_leak_handlers() -> None:
    configure_logging("INFO", "test-service", environment="local", console_stream=io.StringIO())
    shutdown_logging()
    configure_logging("INFO", "test-service", environment="local", console_stream=io.StringIO())

    handlers = [h for h in logging.getLogger().handlers if isinstance(h, LoggingHandler)]
    assert len(handlers) == 1
