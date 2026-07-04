# Example: Minimal App

A complete runnable application lives in
[`examples/minimal/`](https://github.com/dperezcabrera/pico-actuator/tree/main/examples/minimal).
Four files, everything the actuator does:

```
examples/minimal/
  application.yaml        # fastapi + actuator settings
  myapp/
    main.py               # boot: config + pico_boot.init
    controllers.py        # a normal app endpoint (GET /api/hello)
    health.py             # two indicators + one contributor
```

## Boot (`myapp/main.py`)

```python
from pathlib import Path

from fastapi import FastAPI
from pico_boot import init
from pico_ioc import YamlTreeSource, configuration

CONFIG_FILE = Path(__file__).resolve().parent.parent / "application.yaml"


def create_app() -> FastAPI:
    config = configuration(YamlTreeSource(str(CONFIG_FILE)))
    container = init(modules=["myapp"], config=config)
    return container.get(FastAPI)


app = create_app()
```

The only actuator-specific line is... none. `pico_boot.init` reads the
`pico_boot.modules` entry points and pulls in pico-fastapi and pico-actuator.

## Contributions (`myapp/health.py`)

```python
from pico_ioc import component


@component
class PingHealth:  # satisfies HealthIndicator
    name = "ping"

    def check(self):
        return {"status": "UP"}


@component
class DiskHealth:  # async check + detail payload
    name = "disk"

    async def check(self):
        free_mb = 4096
        return {"status": "UP" if free_mb > 100 else "DOWN", "free_mb": free_mb}


@component
class BuildInfo:  # satisfies InfoContributor
    def contribute(self):
        return {"commit": "abc1234", "profile": "demo"}
```

## Run it

```bash
cd examples/minimal
pip install pico-actuator uvicorn
uvicorn myapp.main:app --reload
```

```console
$ curl -s localhost:8000/actuator/health
{"status":"UP","components":{"disk":{"status":"UP","free_mb":4096},"ping":{"status":"UP"}}}

$ curl -s localhost:8000/actuator/info
{"app":"demo-service","build":"2026.06","commit":"abc1234","profile":"demo"}

$ curl -s localhost:8000/api/hello
{"message":"hello from pico-fastapi + pico-actuator"}
```

Swagger UI at `localhost:8000/docs` shows the actuator routes under the
`actuator` tag, next to the app's own `demo` tag.
