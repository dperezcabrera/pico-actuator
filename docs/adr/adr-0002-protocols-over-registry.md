# ADR-002: Protocols over Registry

Status: Accepted

## Context

Applications must be able to contribute health checks and info entries. Spring
Boot solves this with component scanning over known interfaces. In Python the
tempting equivalents are a global registry (`register_indicator(...)`), a
dedicated decorator (`@health_indicator`), or an abstract base class to
inherit from.

pico-ioc already supports collecting all components satisfying a protocol via
`List[Protocol]` constructor injection — the same mechanism pico-fastapi uses
for `List[FastApiConfigurer]`.

## Decision

`HealthIndicator` and `InfoContributor` are `@runtime_checkable` protocols.
Contributing is: implement the protocol, mark the class `@component`. The
controller receives `List[HealthIndicator]` and `List[InfoContributor]` by
constructor injection.

## Consequences

Positive:

- Zero API to import for the common case — no registry, no base class, no
  actuator-specific decorator; indicators depend only on their own code.
- Registration order and duplicate registration are non-issues; the container
  owns the collection.
- Indicators get constructor injection for free (an indicator can depend on an
  `Engine`, a `Redis` client, etc.).

Negative:

- Structural typing fails silently: a class with `checks()` instead of
  `check()` simply is not collected (documented in Troubleshooting).
- Discovering "which indicators are active" requires inspecting the container,
  not grepping for a decorator.

## Alternatives Considered

- Global registry: rejected — global mutable state, import-order sensitivity,
  needs explicit un-registration in tests.
- Dedicated `@health_indicator` decorator: rejected — one more symbol coupling
  app code to the actuator; the protocol already carries the contract.
- ABC inheritance: rejected — forces a base-class import and single
  inheritance slot for what is structurally a duck-typing contract.
