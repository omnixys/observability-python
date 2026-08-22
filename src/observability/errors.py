"""Error classification for observability sinks."""

from __future__ import annotations

from typing import Any

_SERVER_ERROR_THRESHOLD = 500
_CLIENT_ERROR_THRESHOLD = 400


def classify_error(error: Any) -> str:
    """Classify an arbitrary error into a stable bucket.

    Mirrors the TypeScript `ErrorClassifier`:

    - ``server_error``: has an ``status``/``code`` >= 500
    - ``client_error``: has an ``status``/``code`` in 400..499
    - ``internal_error``: any other error
    - ``unknown``: no error given
    """
    if error is None:
        return "unknown"

    status = getattr(error, "status", None)
    if status is None:
        status = getattr(error, "status_code", None)
    if status is None:
        status = getattr(error, "code", None)
    if isinstance(status, int):
        if status >= _SERVER_ERROR_THRESHOLD:
            return "server_error"
        if status >= _CLIENT_ERROR_THRESHOLD:
            return "client_error"

    return "internal_error"


class ErrorClassifier:
    """Callable wrapper around :func:`classify_error` for DI-friendly use."""

    @staticmethod
    def classify(error: Any) -> str:
        return classify_error(error)
