# pico-actuator

Spring Boot-style **actuator** endpoints for the Pico ecosystem, built on top of
[pico-fastapi](https://github.com/dperezcabrera/pico-fastapi) and auto-discovered by
[pico-boot](https://github.com/dperezcabrera/pico-boot).

Install it and the endpoints appear — no wiring:

| Endpoint | Purpose |
|---|---|
| `GET /actuator/health` | Overall status + per-component detail (`200`/`503`) |
| `GET /actuator/health/live` | Liveness — process is responding, touches no deps |
| `GET /actuator/health/ready` | Readiness — aggregate of all health indicators |
| `GET /actuator/info` | Static config + dynamic contributors |
| `GET /actuator/metrics` | Prometheus default registry (needs the `metrics` extra) |
| `POST /actuator/refresh` | Re-reads config sources, publishes `ConfigChanged` (Spring Cloud style) |

## Install

```bash
pip install pico-actuator
```

## 30-second example

```python
# health.py — contribute a component to /actuator/health
from pico_ioc import component
from pico_actuator import HealthIndicator

@component
class DbHealth:  # satisfies HealthIndicator
    name = "db"

    def __init__(self, engine: Engine):
        self.engine = engine

    def check(self):
        self.engine.connect().close()
        return {"status": "UP"}
```

```python
# main.py — boot; pico-boot discovers pico-fastapi + pico-actuator
from fastapi import FastAPI
from pico_boot import init

container = init(modules=["myapp"])
app = container.get(FastAPI)
```

```console
$ curl localhost:8000/actuator/health
{"status":"UP","components":{"db":{"status":"UP"}}}
```

## Next steps

- [Getting Started](getting-started.md) — install, boot, configure
- [User Guide](user-guide/index.md) — indicators and contributors in depth
- [How-To Guides](how-to/index.md) — Kubernetes probes, testing
- [Reference](reference/index.md) — full public API
