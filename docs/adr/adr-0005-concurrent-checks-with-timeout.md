# ADR-005: Concurrent Checks with Per-Indicator Timeout

Status: Accepted

## Context

The first implementation of `health.gather` awaited indicators sequentially
and unbounded. Two failure modes followed: total probe time was the *sum* of
all checks (ten 1-second probes = 10-second health endpoint), and a single
hung `check()` — a database driver waiting on a dead TCP peer — froze
`/health` and `/health/ready` entirely, which under Kubernetes turns a slow
dependency into failed probes for the whole pod.

## Decision

`gather` runs all indicators concurrently via `asyncio.gather`, each wrapped
in `asyncio.timeout` with a budget from `ActuatorSettings.check_timeout_seconds`
(default 5s). Sync `check()` methods execute in a worker thread
(`asyncio.to_thread`) so blocking probes cannot stall the event loop. A
timed-out indicator reports `{"status": "DOWN", "error": "timed out after Ns"}`
— the same failure-isolation contract as ADR-003.

## Consequences

Positive:

- Probe latency is the *slowest* indicator, not the sum; the endpoint has a
  hard upper bound of `check_timeout_seconds`.
- A hung dependency degrades to one `DOWN` component instead of a hung
  endpoint; readiness keeps functioning during the outage.
- Blocking (sync) indicators no longer freeze concurrent requests.

Negative:

- A timed-out **sync** check keeps occupying its worker thread until it
  returns on its own — Python threads are not cancellable. Repeated timeouts
  against a hung dependency can accumulate threads; async checks do not have
  this problem (documented in Troubleshooting and the cookbook).
- Indicators can no longer assume they run alone; one holding a non-reentrant
  resource shared with another indicator must synchronize itself.

## Alternatives Considered

- Sequential with global deadline: rejected — one slow check still starves the
  rest of the budget, and ordering becomes significant.
- Process-pool execution for cancellability: rejected — heavyweight for a
  health probe; serialization constraints on indicators would leak into user
  code.
- No timeout, document "keep checks fast": rejected — the framework can
  enforce the bound; pushing it onto every indicator author guarantees someone
  forgets.
