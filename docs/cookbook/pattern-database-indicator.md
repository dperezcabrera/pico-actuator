# Cookbook: Database Health Indicator

Goal: report the database under `/actuator/health` using a real round-trip,
without holding connections or blocking the event loop.

Key features: `HealthIndicator` protocol, constructor injection, sync `check()`
in a threadpool-friendly form.

## The Pattern

1. Inject the `Engine` (or session factory) through the constructor — the
   indicator is a normal component.
2. Execute the cheapest possible round-trip (`SELECT 1`), not an ORM query.
3. Let exceptions propagate: the actuator's failure isolation turns them into
   `{"status": "DOWN", "error": ...}` for this component only ([ADR-003](../adr/adr-0003-failure-isolation.md)).
4. Return latency as detail — free diagnostic data for dashboards.

## Example

```python
import time

from pico_ioc import component
from sqlalchemy import Engine, text


@component
class DatabaseHealth:
    name = "db"

    def __init__(self, engine: Engine):
        self.engine = engine

    def check(self):
        start = time.perf_counter()
        with self.engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        latency_ms = round((time.perf_counter() - start) * 1000, 1)
        return {"status": "UP", "latency_ms": latency_ms}
```

```console
$ curl -s localhost:8000/actuator/health
{"status":"UP","components":{"db":{"status":"UP","latency_ms":2.3}}}
```

## Notes

- **Sync is fine.** `gather` accepts sync `check()`; for an async driver
  (asyncpg, aiomysql) write `async def check()` instead — both mix freely.
- **Do not cache the connection.** `with engine.connect()` borrows from the
  pool and returns it; a held connection leaks pool capacity for the lifetime
  of the singleton indicator.
- **Timeout at the driver too.** The actuator already bounds each check with
  `check_timeout_seconds`, but a short `connect_timeout` on the engine frees
  the worker thread sooner — a timed-out sync check keeps its thread until the
  driver gives up (see [Troubleshooting](../troubleshooting.md)).
