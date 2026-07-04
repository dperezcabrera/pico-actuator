# Getting Started

## Prerequisites

- Python 3.11+
- A pico-fastapi application booted through pico-boot

## Install

```bash
pip install pico-actuator
```

That is all the wiring there is: pico-actuator registers itself through the
`pico_boot.modules` entry point, so any app booted with `pico_boot.init()` picks
it up automatically.

## Key concepts

| Concept | What it is |
|---|---|
| `ActuatorController` | Serves `/actuator/health`, `/health/live`, `/health/ready`, `/info` |
| `HealthIndicator` | Protocol: a `@component` with `name` and `check()`; one entry under `components` |
| `InfoContributor` | Protocol: a `@component` with `contribute() -> dict`; merged into `/info` |
| `ActuatorSettings` | `@configured` dataclass, populated from the `actuator` config prefix |

## Boot an app

```python
from pathlib import Path

from fastapi import FastAPI
from pico_boot import init
from pico_ioc import YamlTreeSource, configuration

config = configuration(YamlTreeSource("application.yaml"))
container = init(modules=["myapp"], config=config)
app = container.get(FastAPI)
```

## Configure

```yaml
# application.yaml
actuator:
  enabled: true
  show_components: true       # include per-indicator detail in /health
  check_timeout_seconds: 5.0  # per-indicator time budget
  info:                       # static /info entries
    app: my-service
    build: "2026.06"
```

## Add a health indicator

```python
from pico_ioc import component

@component
class DiskHealth:
    name = "disk"

    async def check(self):  # sync or async
        free_mb = shutil.disk_usage("/").free // 2**20
        return {"status": "UP" if free_mb > 100 else "DOWN", "free_mb": free_mb}
```

No registration: pico-ioc collects every `@component` satisfying the protocol via
`List[HealthIndicator]` injection.

## Try it

A complete runnable app lives in
[`examples/minimal/`](https://github.com/dperezcabrera/pico-actuator/tree/main/examples/minimal):

```bash
cd examples/minimal
uvicorn myapp.main:app --reload
curl localhost:8000/actuator/health
```
