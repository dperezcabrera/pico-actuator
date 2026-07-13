# pico-actuator

[![PyPI](https://img.shields.io/pypi/v/pico-actuator.svg)](https://pypi.org/project/pico-actuator/)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/dperezcabrera/pico-actuator)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
![CI (tox matrix)](https://github.com/dperezcabrera/pico-actuator/actions/workflows/ci.yml/badge.svg)
[![codecov](https://codecov.io/gh/dperezcabrera/pico-actuator/branch/main/graph/badge.svg)](https://codecov.io/gh/dperezcabrera/pico-actuator)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=dperezcabrera_pico-actuator&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=dperezcabrera_pico-actuator)
[![Duplicated Lines (%)](https://sonarcloud.io/api/project_badges/measure?project=dperezcabrera_pico-actuator&metric=duplicated_lines_density)](https://sonarcloud.io/summary/new_code?id=dperezcabrera_pico-actuator)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=dperezcabrera_pico-actuator&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=dperezcabrera_pico-actuator)
[![Docs](https://img.shields.io/badge/Docs-pico--actuator-blue?style=flat&logo=readthedocs&logoColor=white)](https://dperezcabrera.github.io/pico-actuator/)
[![Interactive Lab](https://img.shields.io/badge/Learn-online-green?style=flat&logo=python&logoColor=white)](https://dperezcabrera.github.io/pico-learn/)

Spring Boot-style **actuator** endpoints for the [Pico](https://github.com/dperezcabrera/pico-ioc) ecosystem,
built on top of [pico-fastapi](https://github.com/dperezcabrera/pico-fastapi).

Auto-discovered by [pico-boot](https://github.com/dperezcabrera/pico-boot) — install it and the endpoints appear:

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
# optional Prometheus /metrics:  pip install pico-actuator[metrics]
```

## Use

Contribute health by implementing `HealthIndicator` and marking it `@component`.
No registration, no wiring — pico-ioc collects them via `List[HealthIndicator]`:

```python
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

`check()` may be sync or async; return a dict (`{"status": "UP", ...}`) or a
truthy value. Indicators run concurrently, each under a configurable timeout
(`actuator.check_timeout_seconds`, default 5s). A raising or hanging indicator
is reported `DOWN` in isolation — it never takes the endpoint down.

Add `/info` data the same way with `InfoContributor`, or statically via config:

```yaml
# application.yaml
actuator:
  enabled: true
  show_components: true
  info:
    app: my-service
    build: "2026.06"
```

## Documentation

Full docs at **[dperezcabrera.github.io/pico-actuator](https://dperezcabrera.github.io/pico-actuator/)** — getting started, user guide, how-to guides, API reference.

## Built for AI-assisted development

pico-actuator is part of an ecosystem designed for humans and coding agents building software together. Every package ships `AGENTS.md` working conventions, an `llms.txt` machine-readable docs index and documented behaviour pinned by regression tests; [pico-testing](https://github.com/dperezcabrera/pico-testing) gives agents a verification loop for their own changes, and releases are gated by the whole ecosystem booting together against real infrastructure. The full story: [Built for AI-assisted development](https://github.com/dperezcabrera/pico-ioc#built-for-ai-assisted-development).

Install the agent skills for [Claude Code](https://code.claude.com) or [OpenAI Codex](https://openai.com/index/introducing-codex/):

```bash
curl -sL https://raw.githubusercontent.com/dperezcabrera/pico-skills/main/install.sh | bash -s -- actuator
```

## Why

`pico-ioc` already exposes `@health`/`@cleanup` lifecycle primitives but nothing
*serves* them. This package is the thin layer that turns them into operable
HTTP endpoints — the one observability piece you can't improvise in ten lines.

## License

MIT
