"""Probes must be reachable without credentials (structural marker)."""

from pico_actuator.controller import ActuatorController


def test_health_probes_allow_anonymous():
    assert getattr(ActuatorController.health, "_pico_allow_anonymous", False)
    assert getattr(ActuatorController.liveness, "_pico_allow_anonymous", False)
    assert getattr(ActuatorController.readiness, "_pico_allow_anonymous", False)


def test_mutating_and_detailed_endpoints_stay_protected():
    for fn in (ActuatorController.refresh, ActuatorController.metrics, ActuatorController.info):
        assert not getattr(fn, "_pico_allow_anonymous", False)
