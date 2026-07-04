Read and follow ./AGENTS.md for project conventions.

## Pico Ecosystem Context

pico-actuator serves Spring Boot-style `/actuator/*` endpoints over pico-fastapi. It uses:
- `@controller`/`@get` from pico-fastapi for the endpoints (no hand-rolled `APIRouter`)
- `@configured` for `ActuatorSettings` (prefix `actuator`)
- `List[Protocol]` injection to collect `HealthIndicator`/`InfoContributor` components
- Auto-discovered via `pico_boot.modules` entry point

## Key Reminders

- pico-ioc dependency: `>= 2.2.0`; pico-fastapi: `>= 0.2.0`
- **NEVER change `version_scheme`** in pyproject.toml. It MUST remain `"post-release"`. Changing it to `"guess-next-dev"` causes `.dev0` versions to leak to PyPI.
- requires-python >= 3.11
- Commit messages: one line only
- `health.py` must stay pure (no FastAPI / pico-ioc imports)
- Internal pico-ioc attributes: `_pico_meta`, `_pico_infra` (not dunder versions)
