"""Smoke test - verifies omnixys-observability can be imported."""

from __future__ import annotations

import importlib



def test_package_importable() -> None:
    mod = importlib.import_module("omnixys_observability")
    assert hasattr(mod, "__version__")
    assert mod.__version__ == "1.0.0"


def test_public_api() -> None:
    from omnixys_observability import logging, metrics, tracing

    assert logging is not None
    assert metrics is not None
    assert tracing is not None
