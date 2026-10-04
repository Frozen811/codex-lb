from __future__ import annotations

from types import SimpleNamespace

import pytest

from app.core.openai import host_models

pytestmark = pytest.mark.unit


def test_image_host_prefers_image_capable_current_model(monkeypatch) -> None:
    registry = SimpleNamespace(
        plan_types_for_model=lambda model: {"gpt-5.6-sol"} if model == "gpt-5.6-sol" else set(),
        is_suppressed_model=lambda model: False,
    )
    monkeypatch.setattr(host_models, "get_model_registry", lambda: registry)

    assert host_models.resolve_image_host_model() == "gpt-5.6-sol"


def test_image_host_falls_back_when_preferred_model_is_unavailable(monkeypatch) -> None:
    registry = SimpleNamespace(
        plan_types_for_model=lambda model: {"available"} if model == "gpt-6-astra" else set(),
        is_suppressed_model=lambda model: False,
    )
    monkeypatch.setattr(host_models, "get_model_registry", lambda: registry)

    assert host_models.resolve_image_host_model() == "gpt-6-astra"


@pytest.mark.parametrize("fallback_visible", [False, True])
def test_images_exclude_luna_without_changing_probe_host(monkeypatch, fallback_visible: bool) -> None:
    visible = {"gpt-5.6-luna"}
    if fallback_visible:
        visible.add("gpt-5.5")
    registry = SimpleNamespace(
        plan_types_for_model=lambda model: {"plus"} if model in visible else set(),
        is_suppressed_model=lambda model: False,
    )
    monkeypatch.setattr(host_models, "get_model_registry", lambda: registry)

    assert host_models.resolve_default_host_model() == "gpt-5.6-luna"
    assert host_models.resolve_image_host_model() == ("gpt-5.5" if fallback_visible else "gpt-5.6-sol")


def test_images_skip_suppressed_compatible_hosts(monkeypatch) -> None:
    registry = SimpleNamespace(
        plan_types_for_model=lambda model: {"plus"},
        is_suppressed_model=lambda model: model in {"gpt-5.6-sol", "gpt-6-astra"},
    )
    monkeypatch.setattr(host_models, "get_model_registry", lambda: registry)

    assert host_models.resolve_image_host_model() == "gpt-5.5"
