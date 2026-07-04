"""Configuration primitives for pico-actuator.

Defines :class:`ActuatorSettings` (loaded from the ``actuator`` config prefix)
and the :class:`HealthIndicator` / :class:`InfoContributor` protocols. Both
protocols mirror the ``FastApiConfigurer`` idiom in pico-fastapi: implement the
protocol, mark the class ``@component``, and it is auto-collected by pico-ioc
via ``List[...]`` injection.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Protocol, runtime_checkable

from pico_ioc import configured


@runtime_checkable
class HealthIndicator(Protocol):
    """A component contributing one entry to ``/actuator/health``.

    Attributes:
        name: Stable key shown under ``components`` in the health payload.

    The ``check`` method may be sync or async and may return either a mapping
    (``{"status": "UP", ...}``) or a plain truthy/falsy value.
    """

    name: str

    def check(self) -> Dict[str, Any] | bool:
        """Probe the dependency. Return a mapping or a truthy value for UP."""
        ...


@runtime_checkable
class InfoContributor(Protocol):
    """A component contributing key/values to ``/actuator/info``."""

    def contribute(self) -> Dict[str, Any]:
        """Return a mapping merged into the /info payload."""
        ...


@configured(target="self", prefix="actuator", mapping="tree")
@dataclass
class ActuatorSettings:
    """Type-safe actuator settings, populated from the ``actuator`` prefix.

    Mirrors ``FastApiSettings`` in pico-fastapi.

    Attributes:
        enabled: Master switch for the actuator endpoints.
        show_components: Include per-indicator detail in ``/health``.
        check_timeout_seconds: Per-indicator time budget; a slower ``check()``
            reports ``DOWN`` with a timeout error instead of hanging the endpoint.
        info: Static key/values exposed by ``/info`` (build, git sha, ...).

    Example:
        .. code-block:: yaml

            # application.yaml
            actuator:
              enabled: true
              show_components: true
              check_timeout_seconds: 5.0
              info:
                app: my-service
                build: "2026.06"
    """

    enabled: bool = True
    show_components: bool = True
    check_timeout_seconds: float = 5.0
    info: Dict[str, Any] = field(default_factory=dict)
