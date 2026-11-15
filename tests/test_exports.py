"""The public API is exactly what ``__all__`` declares (stability contract)."""

import pico_actuator


def test_public_api_is_declared_and_importable():
    assert set(pico_actuator.__all__) == {
        "ActuatorController",
        "ActuatorSettings",
        "HealthIndicator",
        "InfoContributor",
        "PicoActuatorError",
    }
    for name in pico_actuator.__all__:
        assert getattr(pico_actuator, name) is not None
