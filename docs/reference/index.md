# API Reference

Complete reference for pico-actuator's public API.

## Module: pico_actuator

### Endpoints

| Endpoint | Handler | Status codes |
|---|---|---|
| `GET /actuator/health` | `ActuatorController.health` | `200` UP / `503` DOWN |
| `GET /actuator/health/live` | `ActuatorController.liveness` | `200` always |
| `GET /actuator/health/ready` | `ActuatorController.readiness` | `200` UP / `503` DOWN |
| `GET /actuator/info` | `ActuatorController.info` | `200` |
| `GET /actuator/metrics` | `ActuatorController.metrics` | `200` (OpenMetrics or text 0.0.4 per `Accept`), `501` without the `metrics` extra |

### Protocols

| Protocol | Contract |
|---|---|
| `HealthIndicator` | `name: str`, `check() -> dict | bool` (sync or async) |
| `InfoContributor` | `contribute() -> dict` |

### Classes

| Class | Description |
|---|---|
| `ActuatorController` | pico-fastapi controller serving the endpoints |
| `ActuatorSettings` | `@configured` dataclass, prefix `actuator` |

### Exceptions

| Exception | Description |
|---|---|
| `PicoActuatorError` | Base exception for the package |

See [Configuration](config.md) for the generated API docs.
