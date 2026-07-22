"""Smoke test - verifies omnixys-observability can be imported."""

from __future__ import annotations

import importlib
from importlib.metadata import version as pkg_version


def test_package_importable() -> None:
    mod = importlib.import_module("omnixys_observability")
    assert hasattr(mod, "__version__")
    assert mod.__version__ == pkg_version("omnixys-observability")


def test_public_api() -> None:
    from omnixys_observability import logging, metrics, tracing

    assert logging is not None
    assert metrics is not None
    assert tracing is not None
