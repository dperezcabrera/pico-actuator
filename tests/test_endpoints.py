"""End-to-end: the controller served by a real pico-boot + pico-fastapi app."""

import sys

import pytest

from tests.conftest import FlakyHealth


def test_health_up(client):
    r = client.get("/actuator/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "UP"
    assert body["components"]["ping"]["status"] == "UP"


def test_health_down_returns_503(client):
    FlakyHealth.up = False
    r = client.get("/actuator/health")
    assert r.status_code == 503
    assert r.json()["components"]["flaky"]["status"] == "DOWN"


def test_liveness_always_up(client):
    FlakyHealth.up = False
    r = client.get("/actuator/health/live")
    assert r.status_code == 200
    assert r.json() == {"status": "UP"}


def test_readiness_tracks_indicators(client):
    assert client.get("/actuator/health/ready").status_code == 200
    FlakyHealth.up = False
    assert client.get("/actuator/health/ready").status_code == 503


def test_info_merges_contributors(client):
    r = client.get("/actuator/info")
    assert r.status_code == 200
    assert r.json()["commit"] == "test-sha"


def test_metrics_with_prometheus(client):
    pytest.importorskip("prometheus_client")
    r = client.get("/actuator/metrics")
    assert r.status_code == 200
    assert "python_info" in r.text  # default registry content


def test_metrics_exposition_is_valid_prometheus_format(client):
    parser = pytest.importorskip("prometheus_client.parser")
    r = client.get("/actuator/metrics")
    assert r.status_code == 200
    families = list(parser.text_string_to_metric_families(r.text))
    assert families, "empty exposition"
    names = [f.name for f in families]
    assert len(names) == len(set(names)), "duplicate metric families break scraping"


def test_metrics_honors_openmetrics_accept_header(client):
    pytest.importorskip("prometheus_client")
    r = client.get(
        "/actuator/metrics",
        headers={"Accept": "application/openmetrics-text; version=1.0.0; charset=utf-8"},
    )
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("application/openmetrics-text")
    assert r.text.rstrip().endswith("# EOF")  # OpenMetrics mandatory terminator


def test_metrics_without_prometheus(client, monkeypatch):
    monkeypatch.setitem(sys.modules, "prometheus_client", None)  # force ImportError
    r = client.get("/actuator/metrics")
    assert r.status_code == 501
    assert "pico-actuator[metrics]" in r.json()["detail"]


def test_enabled_false_disables_every_endpoint():
    from fastapi import FastAPI
    from pico_boot import init
    from pico_ioc import DictSource, configuration
    from starlette.testclient import TestClient

    cfg = configuration(DictSource({"fastapi": {"title": "t"}, "actuator": {"enabled": False}}))
    container = init(modules=["pico_fastapi", "pico_actuator"], config=cfg)
    with TestClient(container.get(FastAPI)) as c:
        for path in ("/health", "/health/live", "/health/ready", "/info", "/metrics"):
            assert c.get(f"/actuator{path}").status_code == 404, path
        assert c.post("/actuator/refresh").status_code == 404


def test_refresh_reports_changed_prefixes():
    from fastapi import FastAPI
    from pico_boot import init
    from pico_ioc import DictSource, configuration
    from starlette.testclient import TestClient

    data = {"fastapi": {"title": "t"}, "app": {"greeting": "hola"}}
    cfg = configuration(DictSource(data))
    container = init(modules=["pico_fastapi", "pico_actuator"], config=cfg)
    with TestClient(container.get(FastAPI)) as c:
        assert c.post("/actuator/refresh").json() == {"changed": []}
        data["app"]["greeting"] = "hello"
        r = c.post("/actuator/refresh")
        assert r.status_code == 200
        assert r.json() == {"changed": ["app"]}
