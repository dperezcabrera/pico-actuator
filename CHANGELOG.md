# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-07-02

### Added

- `ActuatorController` exposing `GET /actuator/health`, `/actuator/health/live`,
  `/actuator/health/ready` and `/actuator/info` via pico-fastapi.
- `HealthIndicator` protocol — `@component` classes are auto-collected through
  `List[HealthIndicator]` injection; `check()` may be sync or async and return a
  dict or a truthy value. A raising indicator reports `DOWN` in isolation.
- `InfoContributor` protocol for dynamic `/actuator/info` entries.
- `ActuatorSettings` (`@configured`, prefix `actuator`): `enabled`,
  `show_components`, static `info` map, and `check_timeout_seconds`
  (default `5.0`): per-indicator time budget; a slower check reports `DOWN`
  with a timeout error.
- `GET /actuator/metrics`: Prometheus default-registry exposition behind the
  `metrics` extra; answers `501` when prometheus-client is not installed.
  Honors the `Accept` header: `application/openmetrics-text` gets an
  OpenMetrics exposition (with the mandatory `# EOF` terminator), anything
  else gets Prometheus text 0.0.4. Format validity is pinned by a test using
  the official parser.
- Health indicators run concurrently, each under its own timeout; sync
  `check()` methods execute in a worker thread so a blocking probe cannot
  stall the event loop. `actuator.enabled: false` disables every endpoint
  (each `/actuator/*` route answers `404`).
- Auto-discovery through the `pico_boot.modules` entry point.
- Minimal runnable example under `examples/minimal/`.

[Unreleased]: https://github.com/dperezcabrera/pico-actuator/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/dperezcabrera/pico-actuator/releases/tag/v0.1.0
