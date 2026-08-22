"""Behavioral tests for the observability error classifier."""

from __future__ import annotations

from observability import ErrorClassifier, classify_error


class _StatusError:
    def __init__(self, status: int) -> None:
        self.status = status


class _CodeError:
    def __init__(self, code: int) -> None:
        self.code = code


def test_classify_none() -> None:
    assert classify_error(None) == "unknown"


def test_classify_plain_exception_is_internal() -> None:
    assert classify_error(RuntimeError("boom")) == "internal_error"


def test_classify_server_errors() -> None:
    assert classify_error(_StatusError(500)) == "server_error"
    assert classify_error(_StatusError(503)) == "server_error"
    assert classify_error(_CodeError(502)) == "server_error"


def test_classify_client_errors() -> None:
    assert classify_error(_StatusError(404)) == "client_error"
    assert classify_error(_StatusError(400)) == "client_error"
    assert classify_error(_CodeError(409)) == "client_error"


def test_classify_status_code_attribute() -> None:
    class _Status:
        status_code = 401

    assert classify_error(_Status()) == "client_error"


def test_classifier_class_static() -> None:
    assert ErrorClassifier.classify(None) == "unknown"
    assert ErrorClassifier.classify(_StatusError(500)) == "server_error"
