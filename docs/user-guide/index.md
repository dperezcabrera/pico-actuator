# User Guide

## Health indicators

A health indicator is any `@component` whose class satisfies the
`HealthIndicator` protocol:

```python
from pico_ioc import component

@component
class RedisHealth:
    name = "redis"                    # key under "components"

    def __init__(self, redis: Redis): # constructor injection works
        self.redis = redis

    def check(self):
        self.redis.ping()
        return {"status": "UP"}
```

### Return values

`check()` may be **sync or async** and return:

- a mapping — `{"status": "UP", "free_mb": 4096}`; missing `status` defaults to `UP`
- a plain truthy/falsy value — `True` → `UP`, `False` → `DOWN`

### Failure isolation

A raising indicator is reported as its own `DOWN` component with the error
message — it never turns the endpoint into a 500:

```json
{"status": "DOWN", "components": {"redis": {"status": "DOWN", "error": "connection refused"}}}
```

### Concurrency and timeouts

Indicators run **concurrently** — total probe time is the slowest indicator,
not the sum. Each `check()` gets its own time budget
(`actuator.check_timeout_seconds`, default 5s); exceeding it reports
`{"status": "DOWN", "error": "timed out after 5.0s"}` for that component only.
Sync checks execute in a worker thread, so a blocking probe never freezes the
event loop.

### Overall status

The overall status is `DOWN` if **any** component is `DOWN`, else `UP`.
`/actuator/health` and `/actuator/health/ready` answer `503` when `DOWN`,
`200` when `UP`. `/actuator/health/live` always answers `UP` — it proves the
process responds, nothing more.

## Info contributors

Same idiom for `/actuator/info`:

```python
@component
class GitInfo:
    def contribute(self):
        return {"commit": read_git_sha(), "branch": "main"}
```

Dynamic contributions are merged **over** the static `actuator.info` map from
configuration.

## Settings

```yaml
actuator:
  enabled: true               # master switch
  show_components: true       # per-indicator detail in /health
  check_timeout_seconds: 5.0  # per-indicator time budget
  info:
    app: my-service
```

`ActuatorSettings` is a `@configured` dataclass — inject it anywhere you need
programmatic access to these values.
