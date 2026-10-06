from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize("filename", ["docker-compose.yml", "docker-compose.prod.yml"])
def test_default_compose_does_not_reserve_native_oauth_callback_port(filename):
    document = yaml.safe_load((ROOT / filename).read_text(encoding="utf-8"))
    assert document["services"]["server"]["ports"] == ["2455:2455"]


def test_explicit_callback_overlay_publishes_only_host_loopback():
    document = yaml.safe_load((ROOT / "deploy/docker/docker-compose.oauth.yml").read_text(encoding="utf-8"))
    assert document["services"]["server"]["ports"] == ["127.0.0.1:1455:1455"]


def test_basic_run_examples_leave_callback_port_free():
    document = (ROOT / "docs/deployment/docker.md").read_text(encoding="utf-8")
    basic = document.split("## Basic run", 1)[1].split("## Switching Wi-Fi", 1)[0]
    assert "-p 1455:1455" not in basic
    assert "manual" in basic.lower()
    assert "device" in basic.lower()
