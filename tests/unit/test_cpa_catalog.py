from __future__ import annotations

from app.modules.model_sources.catalog import (
    clear_cpa_catalog_snapshots,
    get_cpa_catalog_snapshot,
    parse_cpa_catalog_payload,
    store_cpa_catalog_snapshot,
    sync_cpa_catalog_models,
)


def test_parse_cpa_catalog_payload_standard_openai_format() -> None:
    payload = {
        "data": [
            {"id": "cpa-model-a", "object": "model"},
            {"id": "cpa-model-b", "object": "model"},
        ]
    }
    models = parse_cpa_catalog_payload(payload)
    assert models == ["cpa-model-a", "cpa-model-b"]


def test_parse_cpa_catalog_payload_list_format() -> None:
    payload = ["cpa-model-1", {"id": "cpa-model-2"}]
    models = parse_cpa_catalog_payload(payload)
    assert models == ["cpa-model-1", "cpa-model-2"]


def test_parse_cpa_catalog_payload_invalid_empty() -> None:
    assert parse_cpa_catalog_payload({}) == []
    assert parse_cpa_catalog_payload(None) == []


def test_sync_cpa_catalog_models_retains_unavailable_ownership() -> None:
    clear_cpa_catalog_snapshots()
    source_id = "src_cpa_1"
    existing_models = [
        {"model": "model-active", "is_enabled": True},
        {"model": "model-to-disappear", "is_enabled": True},
    ]
    # Upstream now only returns model-active and a new model
    discovered = ["model-active", "model-new"]

    synced = sync_cpa_catalog_models(source_id, existing_models, discovered)

    # model-to-disappear must be retained with is_enabled=False to preserve ownership
    model_map = {m["model"]: m for m in synced}
    assert "model-to-disappear" in model_map
    assert model_map["model-to-disappear"]["is_enabled"] is False

    assert "model-active" in model_map
    assert model_map["model-active"]["is_enabled"] is True

    assert "model-new" in model_map
    assert model_map["model-new"]["is_enabled"] is True

    # Snapshot is stored
    snapshot = get_cpa_catalog_snapshot(source_id)
    assert snapshot is not None
    assert set(snapshot.models) == {"model-active", "model-new"}


def test_sync_cpa_catalog_models_preserves_snapshot_on_outage() -> None:
    clear_cpa_catalog_snapshots()
    source_id = "src_cpa_2"
    existing_models = [
        {"model": "model-1", "is_enabled": True},
        {"model": "model-2", "is_enabled": False},
    ]
    store_cpa_catalog_snapshot(source_id, ["model-1"])

    # Outage represented by None discovered models
    synced = sync_cpa_catalog_models(source_id, existing_models, None)
    assert synced == existing_models

    snapshot = get_cpa_catalog_snapshot(source_id)
    assert snapshot is not None
    assert snapshot.models == ("model-1",)
