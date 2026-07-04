# ADR-001: Reuse pico-fastapi Controllers

Status: Accepted

## Context

The actuator needs to expose HTTP endpoints inside an existing pico-fastapi
application. FastAPI's native mechanism for a pluggable set of routes is an
`APIRouter` that the host app includes explicitly. pico-fastapi, however,
already defines a `@controller` decorator whose classes are discovered from the
container and registered automatically, with constructor injection resolved by
pico-ioc.

## Decision

`ActuatorController` is a plain pico-fastapi `@controller(prefix="/actuator")`.
No `APIRouter`, no `include_router` step, no mount hook.

## Consequences

Positive:

- Route wiring, DI resolution and result normalization (the `(body, status)`
  tuple convention) are inherited — zero integration code.
- The controller is a regular component: tests and applications can override or
  replace it in the container like any other component.
- Discovery is uniform: installing the package is enough, because pico-boot
  imports the module and pico-fastapi picks up the controller.

Negative:

- Hard dependency on pico-fastapi; the actuator cannot serve over a bare
  FastAPI or Starlette app.
- The `/actuator` prefix is fixed at class-decoration time, not configurable
  per deployment (acceptable: it is the ecosystem-wide convention).

## Alternatives Considered

- Plain `APIRouter` + manual `include_router`: rejected — requires an
  integration step in every host app, defeating auto-discovery.
- ASGI middleware answering `/actuator/*` before routing: rejected — bypasses
  DI, duplicates response serialization, invisible in the OpenAPI schema.
