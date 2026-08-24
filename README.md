# omnixys-observability

Omnixys shared observability package — OpenTelemetry tracing, structlog structured logging, Prometheus metrics, request-context propagation and error classification.

## Installation

```bash
pip install omnixys-observability
```

## Features

- **Tracing**: OTLP HTTP trace export with ratio/always-on sampling, FastAPI/httpx/logging auto-instrumentation, and a `@span` decorator for functions and methods
- **Logging**: structlog JSON (or colored pretty) console output, OTLP log export, context enrichment (request/correlation id, user, tenant, trace ids), and recursive secret redaction
- **Metrics**: Prometheus counters/histograms/gauges for HTTP, GraphQL, DB, Kafka, cache, rate limiting, auth and outbox — plus `RateLimitMetrics` and `SloMetrics` helpers
- **Request context**: contextvars-based `RequestContext` propagation across async boundaries
- **Errors**: `classify_error()`/`ErrorClassifier` buckets into `server_error` / `client_error` / `internal_error`
- **Runtime**: `configure_observability()` one-call setup of traces + logs with a shared service resource

## Usage

### One-call setup

```python
from observability import configure_observability, shutdown_observability

configure_observability(
    service_name="ticketing",
    otlp_endpoint="http://collector:4318",
    environment="production",
)
```

### Structured logging

```python
from observability import configure_logging, get_logger, RequestContext, set_request_context

configure_logging("INFO", service_name="ticketing")

set_request_context(RequestContext(request_id="r1", user_id="u1", tenant_id="t1"))
log = get_logger("ticketing")
log.info("event_created", event_id="e1")
log.error("payment_failed", status=503, token="sk_live_...")  # token -> [REDACTED]
```

`LOG_PRETTY=true` forces colored console output; production defaults to JSON.

#### Console vs. Loki levels

The console threshold and the OTLP (Loki) threshold are independent:

- `configure_logging("INFO", ...)` keeps the console at `INFO`.
- The OTLP export defaults to `DEBUG`, so debug logs still appear in
  Grafana/Loki in production while the console stays quiet.

Override the Loki threshold via the `OTEL_LOG_LEVEL` environment variable or
the `otel_log_level` parameter (values: `TRACE`, `DEBUG`, `INFO`, `WARNING`,
`ERROR`; invalid values fall back to `DEBUG`):

```bash
OTEL_LOG_LEVEL=WARNING   # Loki receives WARNING and above only
```

```python
configure_logging("INFO", service_name="ticketing", otel_log_level="DEBUG")
```

### Spans

```python
from observability import span

@span
async def process_event(event_id: str) -> None: ...

@span(name="billing.charge", attributes={"provider": "stripe"})
def charge(customer_id: str) -> None: ...
```

### Metrics

```python
from observability import SloMetrics, RateLimitMetrics, http_requests_total

http_requests_total.labels(method="POST", path="/events", status_code="201").inc()

slo = SloMetrics()
slo.record_success()
slo.record_error()
slo.error_rate()          # 0.5

rl = RateLimitMetrics()
rl.hit("sms:user:42")
rl.get("sms:user:42")     # 1
```

### Error classification

```python
from observability import classify_error

classify_error(HTTPException(status_code=503))   # "server_error"
classify_error(HTTPException(status_code=404))   # "client_error"
classify_error(RuntimeError("boom"))             # "internal_error"
```

## Testing

```bash
uv run pytest -q          # 30 tests
uv run ruff check .       # lint
uv run mypy src/          # strict typing
```

## License

GPL-3.0-or-later
