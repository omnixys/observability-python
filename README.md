# omnixys-observability

Omnixys shared observability package with OpenTelemetry tracing, structured logging, and Prometheus metrics.

## Installation

```bash
pip install omnixys-observability
```

## Features

- OpenTelemetry distributed tracing
- Structured logging with structlog
- Prometheus metrics collection
- FastAPI instrumentation
- Request context propagation

## Usage

```python
from omnixys_observability import configure_logging, configure_tracing, instrument_fastapi
```

## License

GPL-3.0-or-later
