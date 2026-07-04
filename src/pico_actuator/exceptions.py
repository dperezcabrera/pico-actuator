"""Custom exceptions for pico-actuator."""


class PicoActuatorError(Exception):
    """Base exception for all pico-actuator errors.

    Catch this at startup boundaries to handle any pico-actuator failure
    without matching individual subclasses.
    """
