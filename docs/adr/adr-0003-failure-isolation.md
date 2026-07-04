# ADR-003: Failure Isolation in Health Checks

Status: Accepted

## Context

A health endpoint aggregates probes against external dependencies — precisely
the code most likely to raise (timeouts, connection refused, auth expiry). If
one indicator's exception propagates, the endpoint answers `500` with no body,
and the operator loses visibility over every *other* component exactly when
they need it most.

## Decision

`health.gather` wraps each indicator individually. A raising indicator is
reported as its own component with `{"status": "DOWN", "error": str(exc)}`;
the overall status turns `DOWN` (HTTP `503`), and all sibling components still
report normally. The endpoint itself never propagates an indicator exception.

## Consequences

Positive:

- The health payload is always well-formed JSON with full per-component
  detail — a monitoring dashboard keeps working during partial outages.
- `503` vs `500` semantics stay clean: `503` means "a dependency is unhealthy",
  `500` would mean "the actuator itself is broken".
- One flaky indicator cannot mask the status of the others.

Negative:

- A programming error inside an indicator (e.g. `AttributeError`) is reported
  as a `DOWN` dependency rather than surfacing as a bug — the `error` string is
  the only clue.
- Exception messages are exposed in the payload; deployments that consider
  them sensitive must secure `/actuator/*` (see the cookbook).

## Alternatives Considered

- Fail-fast (let the exception propagate): rejected — turns partial outages
  into total loss of observability.
- Global try/except returning bare `503` without detail: rejected — hides
  which component failed.
