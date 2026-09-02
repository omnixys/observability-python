"""Smoke test - verifies omnixys-observability can be imported."""

from __future__ import annotations

import importlib
from importlib.metadata import version as pkg_version

from observability import logging, metrics, tracing


def test_package_importable() -> None:
    mod = importlib.import_module("observability")
    assert mod is not None


def test_package_version() -> None:
    assert pkg_version("omnixys-observability")


def test_public_api() -> None:
    assert logging is not None
    assert metrics is not None
    assert tracing is not None
