"""Actuator endpoints.

Reuses pico-fastapi's ``@controller`` / ``@get`` instead of hand-rolling an
``APIRouter``, so route wiring, DI resolution and result normalization are
inherited for free. Dependencies (settings, indicators, contributors) are
constructor-injected; ``List[Protocol]`` injection is the same mechanism
pico-fastapi uses for ``List[FastApiConfigurer]``.
"""

from typing import List

from pico_fastapi import controller, get, post
from pico_ioc import PicoContainer
from starlette.requests import Request
from starlette.responses import Response

from .config import ActuatorSettings, HealthIndicator, InfoContributor
from .health import UP, gather

# What every endpoint answers when the master switch is off. 404 (not 403):
# a disabled actuator should be indistinguishable from an absent one.
_DISABLED = ({"detail": "Not Found"}, 404)


def _allow_anonymous(fn):
    """Structural contract with pico-client-auth: probes must answer without
    credentials (kubelet cannot send JWTs). Only the health trio — info,
    metrics and refresh stay subject to auth when a middleware is active."""
    fn._pico_allow_anonymous = True
    return fn


@controller(prefix="/actuator", tags=["actuator"])
class ActuatorController:
    def __init__(
        self,
        settings: ActuatorSettings,
        indicators: List[HealthIndicator],
        contributors: List[InfoContributor],
        container: PicoContainer,
    ):
        self.settings = settings
        self.indicators = indicators
        self.contributors = contributors
        self.container = container

    async def _gather(self):
        return await gather(self.indicators, timeout=self.settings.check_timeout_seconds)

    @_allow_anonymous
    @get("/health")
    async def health(self):
        """Full health: overall status plus per-component detail."""
        if not self.settings.enabled:
            return _DISABLED
        overall, components = await self._gather()
        body = {"status": overall}
        if self.settings.show_components:
            body["components"] = components
        # (content, status) tuple — pico-fastapi normalizes this to a JSONResponse.
        return body, 200 if overall == UP else 503

    @_allow_anonymous
    @get("/health/live")
    async def liveness(self):
        """Liveness: is the process responding at all? Cheap, touches no deps."""
        if not self.settings.enabled:
            return _DISABLED
        return {"status": UP}

    @_allow_anonymous
    @get("/health/ready")
    async def readiness(self):
        """Readiness: are dependencies healthy? Aggregate of all indicators."""
        if not self.settings.enabled:
            return _DISABLED
        overall, _ = await self._gather()
        return {"status": overall}, 200 if overall == UP else 503

    @get("/info")
    async def info(self):
        """Static config info merged with dynamic contributors."""
        if not self.settings.enabled:
            return _DISABLED
        data = dict(self.settings.info)
        for c in self.contributors:
            data.update(c.contribute())
        return data

    @post("/refresh")
    async def refresh(self):
        """Re-read config sources; report the changed top-level prefixes.

        Mirror of Spring Cloud's ``POST /actuator/refresh``: components
        subscribed to ``ConfigChanged`` re-read their config.
        """
        if not self.settings.enabled:
            return _DISABLED
        return {"changed": sorted(self.container.refresh_config())}

    @get("/metrics")
    async def metrics(self, request: Request):
        """Prometheus/OpenMetrics exposition of the default registry.

        Honors the ``Accept`` header (``application/openmetrics-text`` or
        Prometheus text 0.0.4). Needs the ``metrics`` extra; answers 501
        when prometheus-client is not installed.
        """
        if not self.settings.enabled:
            return _DISABLED
        try:
            from prometheus_client import REGISTRY
            from prometheus_client.exposition import choose_encoder
        except ImportError:
            return {"detail": "prometheus-client not installed; pip install pico-actuator[metrics]"}, 501
        encoder, content_type = choose_encoder(request.headers.get("accept", ""))
        return Response(content=encoder(REGISTRY), media_type=content_type)
