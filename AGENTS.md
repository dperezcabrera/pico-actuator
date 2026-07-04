# pico-actuator

Spring Boot-style actuator endpoints (`/actuator/health`, `/actuator/info`) for pico-fastapi apps. Auto-discovered by pico-boot.

## Commands

```bash
pip install -e ".[dev]"           # Install in dev mode
pytest tests/ -v                  # Run tests
pytest --cov=pico_actuator --cov-report=term-missing tests/  # Coverage
tox                               # Full matrix (3.11-3.14)
mkdocs serve -f mkdocs.yml        # Local docs
```

## Project Structure

```
src/pico_actuator/
  __init__.py          # Public API exports
  controller.py        # ActuatorController - /actuator/health, /health/live, /health/ready, /info
  health.py            # Pure aggregation logic (gather, UP/DOWN) - no FastAPI, no DI
  config.py            # ActuatorSettings, HealthIndicator / InfoContributor protocols
  exceptions.py        # PicoActuatorError
```

## Key Concepts

- **`HealthIndicator`**: `@component` class with `name` attr and `check()` (sync or async, returns dict or truthy). Collected via `List[HealthIndicator]` constructor injection — no registration.
- **`InfoContributor`**: `@component` class with `contribute() -> dict`, merged into `/actuator/info`.
- **`ActuatorSettings`**: `@configured(prefix="actuator")` dataclass — `enabled`, `show_components`, static `info` map.
- **Failure isolation**: a raising indicator reports `{"status": "DOWN", "error": ...}` for its component only; the endpoint never 500s because of one indicator.
- **Concurrency + timeout**: indicators run concurrently via `asyncio.gather`; each check is bounded by `ActuatorSettings.check_timeout_seconds` (default 5s). Sync checks run in a worker thread (`asyncio.to_thread`) — a timed-out sync check keeps its thread until it returns (not cancellable).
- **Metrics**: `GET /actuator/metrics` serves the Prometheus default registry; `501` without the `metrics` extra.
- **Status codes**: `/health` and `/health/ready` return `503` when overall is `DOWN`, else `200`. `/health/live` is always `UP` (process liveness).
- **Auto-discovery**: `pico_boot.modules` entry point; installing the package is enough.

## Code Style

- Python 3.11+
- `health.py` stays pure — no FastAPI or pico-ioc imports (unit-testable without booting)
- Controller reuses pico-fastapi `@controller`/`@get`; never hand-roll an `APIRouter`
- Protocols mirror the `FastApiConfigurer` idiom from pico-fastapi

## Testing

- pytest; aggregation logic tested without an app (`tests/test_health.py`)
- Endpoint tests boot a real container via `pico_boot.init` + `TestClient` (`tests/conftest.py`)
- Target: >95% coverage

## Boundaries

- Do not modify `_version.py`
- No direct dependency on pico-boot (entry point only)
- Keep `health.py` free of framework imports
