# Testing

## Unit-test an indicator

Indicators are plain classes — no framework needed:

```python
def test_disk_health_down_when_full():
    ind = DiskHealth(fake_fs(free_mb=10))
    assert ind.check()["status"] == "DOWN"
```

## Unit-test aggregation

`pico_actuator.health.gather` is pure and importable without FastAPI:

```python
import asyncio
from pico_actuator.health import gather, UP, DOWN

def test_one_down_drags_overall_down():
    overall, components = asyncio.run(gather([up_indicator, broken_indicator]))
    assert overall == DOWN
```

## End-to-end: boot the real app

Boot a container through `pico_boot.init` and hit the endpoints with
Starlette's `TestClient` — this is exactly what
[`tests/conftest.py`](https://github.com/dperezcabrera/pico-actuator/blob/main/tests/conftest.py)
does:

```python
import sys
from fastapi import FastAPI
from pico_boot import init
from starlette.testclient import TestClient

def test_health():
    container = init(modules=[sys.modules[__name__]])  # module defining your @components
    with TestClient(container.get(FastAPI)) as client:
        assert client.get("/actuator/health").status_code == 200
```

Entry-point auto-discovery pulls in pico-fastapi and pico-actuator, so the test
exercises the same wiring as production.
