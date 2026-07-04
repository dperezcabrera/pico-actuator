"""Example health indicators and an info contributor.

Just by being @component classes that satisfy the protocols, these are picked
up by pico-actuator — no registration anywhere.
"""

from pico_ioc import component

from pico_actuator import HealthIndicator, InfoContributor


@component
class PingHealth:  # satisfies HealthIndicator
    name = "ping"

    def check(self):
        return {"status": "UP"}


@component
class DiskHealth:  # async check + detail payload
    name = "disk"

    async def check(self):
        free_mb = 4096  # pretend we stat()'d the volume
        return {"status": "UP" if free_mb > 100 else "DOWN", "free_mb": free_mb}


@component
class BuildInfo:  # satisfies InfoContributor
    def contribute(self):
        return {"commit": "abc1234", "profile": "demo"}
