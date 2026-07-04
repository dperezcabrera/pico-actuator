"""pico-actuator: Spring Boot-style actuator endpoints for pico-fastapi.

Exposes ``/actuator/health`` (+ ``/health/live``, ``/health/ready``) and
``/actuator/info`` by auto-discovery through pico-boot. Applications add
health/info data by implementing :class:`HealthIndicator` /
:class:`InfoContributor` and marking the class ``@component``.

Public API:
    Controller: ActuatorController
    Protocols: HealthIndicator, InfoContributor
    Dataclasses: ActuatorSettings
    Exceptions: PicoActuatorError
"""

from .config import ActuatorSettings, HealthIndicator, InfoContributor
from .controller import ActuatorController
from .exceptions import PicoActuatorError

__all__ = [
    "ActuatorSettings",
    "HealthIndicator",
    "InfoContributor",
    "ActuatorController",
    "PicoActuatorError",
]
