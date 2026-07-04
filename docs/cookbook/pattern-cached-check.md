# Cookbook: Caching Expensive Checks

Goal: keep `/actuator/health` cheap when an indicator's probe is expensive
(cross-region call, rate-limited API, cold storage), without giving up
freshness entirely.

Key features: plain instance state on a singleton component — indicators are
components, so they keep state between probes.

## The Pattern

1. Store the last result and its timestamp on the indicator.
2. Serve the cached result while it is younger than a TTL.
3. Probe again only when stale; on failure the error becomes the fresh result
   (a `DOWN` should not be masked by an old `UP` for long).

## Example

```python
import time

from pico_ioc import component


@component
class LicenseServerHealth:
    name = "license-server"
    TTL_SECONDS = 30

    def __init__(self, client: LicenseClient):
        self.client = client
        self._cached: dict | None = None
        self._checked_at = 0.0

    async def check(self):
        now = time.monotonic()
        if self._cached is not None and now - self._checked_at < self.TTL_SECONDS:
            return self._cached | {"cached": True}
        await self.client.ping()  # raising here reports DOWN, uncached
        self._cached = {"status": "UP"}
        self._checked_at = now
        return self._cached
```

## Notes

- **Failures are not cached** in this form: a raise skips the cache update, so
  the next probe retries immediately. Cache failures too (with a shorter TTL)
  if the dependency punishes retries.
- **Kubernetes multiplies probes.** With `periodSeconds: 5` and liveness +
  readiness + a dashboard, one indicator can be hit several times per second —
  that is what the TTL absorbs.
- **`time.monotonic()`**, not `time.time()` — wall-clock jumps must not
  invalidate (or eternally validate) the cache.
