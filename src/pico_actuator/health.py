"""Health aggregation.

Pure logic on purpose: no FastAPI and no DI here, so it can be unit-tested
without booting an app. The controller layer just calls :func:`gather`.

Indicators run concurrently, each under its own timeout. Sync ``check()``
methods are pushed to a worker thread so a slow blocking probe cannot freeze
the event loop.
"""

import asyncio
import inspect
from typing import TYPE_CHECKING, Any, Dict, List, Tuple

if TYPE_CHECKING:  # avoid importing config (and pico_ioc) just for a type hint
    from .config import HealthIndicator

UP = "UP"
DOWN = "DOWN"

DEFAULT_TIMEOUT = 5.0


async def _result(indicator: "HealthIndicator", timeout: float) -> Dict[str, Any]:
    """Run a single indicator and normalize its outcome into a status dict.

    A raising or timing-out indicator is reported as ``DOWN`` rather than
    propagating, so one broken dependency never takes the whole endpoint down.
    """
    try:
        async with asyncio.timeout(timeout):
            if inspect.iscoroutinefunction(indicator.check):
                res = await indicator.check()
            else:
                # ponytail: a timed-out sync check keeps running in its thread;
                # the endpoint answers anyway. Cancellable probes need async.
                res = await asyncio.to_thread(indicator.check)
                if inspect.isawaitable(res):
                    res = await res
        if isinstance(res, dict):
            res.setdefault("status", UP)
            return res
        return {"status": UP if res else DOWN}
    except TimeoutError:
        return {"status": DOWN, "error": f"timed out after {timeout}s"}
    except Exception as exc:
        return {"status": DOWN, "error": str(exc)}


async def gather(indicators: List["HealthIndicator"], timeout: float = DEFAULT_TIMEOUT) -> Tuple[str, Dict[str, Any]]:
    """Aggregate all indicators into an ``(overall, components)`` pair.

    Indicators are probed concurrently; each gets its own *timeout* seconds.

    Args:
        indicators: The health indicators to probe.
        timeout: Per-indicator time budget in seconds.

    Returns:
        ``overall`` is ``DOWN`` if any component is ``DOWN``, else ``UP``.
        ``components`` maps each indicator name to its status dict.
    """
    results = await asyncio.gather(*(_result(ind, timeout) for ind in indicators))
    components: Dict[str, Any] = {
        getattr(ind, "name", ind.__class__.__name__): res for ind, res in zip(indicators, results)
    }
    overall = DOWN if any(c["status"] == DOWN for c in components.values()) else UP
    return overall, components
