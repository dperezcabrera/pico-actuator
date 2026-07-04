# FAQ

## Do I have to register my indicators somewhere?

No. Any `@component` class satisfying the `HealthIndicator` protocol is
collected automatically via `List[HealthIndicator]` injection.

## Can `check()` be async?

Yes. Sync and async indicators can be mixed freely; awaitables are awaited.

## What happens if an indicator raises?

Its component reports `{"status": "DOWN", "error": "<message>"}` and the
overall status turns `DOWN` (HTTP `503`). The endpoint never returns a 500
because of a broken indicator.

## Why does `/health/live` say UP while my database is down?

By design. Liveness answers "is the process responding?" so that orchestrators
only restart hung processes. Dependency health belongs to `/health/ready`.

## How do I turn the actuator off entirely?

```yaml
actuator:
  enabled: false
```

Every `/actuator/*` endpoint answers `404`, indistinguishable from the package
not being installed.

## How do I hide the per-component detail?

```yaml
actuator:
  show_components: false
```

`/actuator/health` then returns only `{"status": "..."}`.

## Where does `/actuator/info` data come from?

Two sources, merged: the static `actuator.info` map from configuration, then
every `InfoContributor` component (contributors win on key conflicts).

## Does this need pico-boot?

For zero-config discovery, yes — the `pico_boot.modules` entry point does the
wiring. With plain `pico_ioc.init` you can still pass `pico_actuator` in
`modules=` explicitly.

## What if an indicator hangs?

Each indicator runs under a per-check timeout (`actuator.check_timeout_seconds`,
default 5s) and all indicators run concurrently. A slow or hung `check()` —
sync or async — reports `{"status": "DOWN", "error": "timed out after 5.0s"}`
for its component while the endpoint keeps answering.

## Is there a `/metrics` endpoint?

Yes — `GET /actuator/metrics` serves the Prometheus default registry and
honors content negotiation: scrapers asking for
`application/openmetrics-text` get OpenMetrics, everyone else gets Prometheus
text 0.0.4. It needs the `metrics` extra
(`pip install pico-actuator[metrics]`); without prometheus-client installed
it answers `501`.
