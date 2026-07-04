# Architecture Decision Records (ADRs)

This index lists all significant architecture decisions for the `pico-actuator` project. Keep it sorted by ADR number.

ADR Index:

- ADR-001: Reuse pico-fastapi Controllers — Accepted — ./adr-0001-reuse-pico-fastapi-controllers.md
- ADR-002: Protocols over Registry — Accepted — ./adr-0002-protocols-over-registry.md
- ADR-003: Failure Isolation in Health Checks — Accepted — ./adr-0003-failure-isolation.md
- ADR-004: Dependency-Free Liveness — Accepted — ./adr-0004-dependency-free-liveness.md
- ADR-005: Concurrent Checks with Per-Indicator Timeout — Accepted — ./adr-0005-concurrent-checks-with-timeout.md

Status legend:

- Proposed: Under discussion, not yet binding.
- Accepted: Approved and implemented or scheduled for implementation.
- Superseded: Replaced by a newer ADR (referenced in both ADRs).
- Deprecated: No longer recommended, kept for historical context.
- Rejected: Explicitly not adopted.

Contributing a new ADR:

- Use sequential numbering with 4 digits: `adr-XXXX-slug.md`.
- Keep the slug lowercase, words separated by hyphens.
- Start with status Proposed; update to Accepted after approval.
