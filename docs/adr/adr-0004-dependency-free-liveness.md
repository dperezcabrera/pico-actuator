# ADR-004: Dependency-Free Liveness

Status: Accepted

## Context

Kubernetes distinguishes liveness (restart the pod if it fails) from readiness
(remove the pod from the Service if it fails). A widespread anti-pattern is
pointing the liveness probe at a full health check: when a shared dependency
(database, broker) blinks, **every** pod fails liveness simultaneously and the
orchestrator restarts perfectly healthy processes in a loop — a self-inflicted
outage on top of the dependency incident.

## Decision

`GET /actuator/health/live` returns `{"status": "UP"}` unconditionally. It
proves the process answers HTTP — the event loop is alive — and nothing else.
Dependency health is served by `/actuator/health/ready` (aggregate of all
indicators) and `/actuator/health` (aggregate + detail).

## Consequences

Positive:

- Restart storms during dependency outages are impossible by construction.
- The endpoint is allocation-free and safe to poll at high frequency.
- The liveness/readiness split maps one-to-one onto Kubernetes probe semantics
  (documented in the how-to guide).

Negative:

- A deadlocked worker thread can still answer liveness (the event loop
  responds); detecting internal starvation would need a dedicated indicator on
  readiness or an external watchdog.
- Operators expecting Spring Boot's configurable liveness-state machine
  (`LivenessState.BROKEN`) will find no equivalent — by design, for now.

## Alternatives Considered

- Liveness = aggregate of all indicators: rejected — couples pod restarts to
  dependency outages (the anti-pattern above).
- Configurable indicator subset for liveness: rejected for v0.x — YAGNI until
  a real deployment needs it; readiness already covers dependency gating.
