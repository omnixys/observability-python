from __future__ import annotations

from observability.logging import configure_logging, shutdown_logging
from observability.tracing import configure_tracing, shutdown_tracing


def configure_observability(
    *,
    service_name: str,
    otlp_endpoint: str,
    environment: str = "local",
    log_level: str = "INFO",
    tracing_enabled: bool = True,
    logs_enabled: bool = True,
    sampling_probability: float = 0.1,
) -> None:
    """Configure traces and logs with one canonical service resource."""
    configure_tracing(
        service_name=service_name,
        otlp_endpoint=otlp_endpoint,
        environment=environment,
        enabled=tracing_enabled,
        sampling_probability=sampling_probability,
    )
    configure_logging(
        log_level,
        service_name if logs_enabled else None,
        otlp_endpoint=otlp_endpoint,
        environment=environment,
    )


def shutdown_observability() -> None:
    shutdown_logging()
    shutdown_tracing()
