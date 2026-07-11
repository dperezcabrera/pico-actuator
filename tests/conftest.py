"""Shared fixtures: a real container booted through pico-boot.

Isolation from installed plugins comes from the pico-testing plugin;
pico-fastapi and pico-actuator are listed explicitly instead.
"""

import sys

import pytest
from fastapi import FastAPI
from pico_boot import init
from pico_ioc import DictSource, component, configuration
from starlette.testclient import TestClient

CONFIG = configuration(
    DictSource(
        {
            "fastapi": {"title": "test-app"},
            "actuator": {"info": {"app": "test-app"}},
        }
    )
)


@component
class PingHealth:
    name = "ping"

    def check(self):
        return {"status": "UP"}


@component
class FlakyHealth:
    """Toggled by tests to drive the overall status DOWN."""

    name = "flaky"
    up = True

    def check(self):
        if not FlakyHealth.up:
            raise RuntimeError("flaky is down")
        return True


@component
class BuildInfo:
    def contribute(self):
        return {"commit": "test-sha"}


@pytest.fixture()
def client():
    FlakyHealth.up = True
    container = init(modules=["pico_fastapi", "pico_actuator", sys.modules[__name__]], config=CONFIG)
    app = container.get(FastAPI)
    with TestClient(app) as c:
        yield c
