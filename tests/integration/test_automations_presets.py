from __future__ import annotations

import pytest

from app.core.crypto import TokenEncryptor
from app.core.utils.time import utcnow
from app.db.models import Account, AccountStatus
from app.db.session import SessionLocal
from app.modules.accounts.repository import AccountsRepository
from app.modules.automations.presets import (
    WEEKLY_PRESTART_PRESET_ID,
    get_automation_preset,
    list_automation_presets,
)

pytestmark = pytest.mark.integration


async def _create_test_account(account_id: str) -> None:
    encryptor = TokenEncryptor()
    async with SessionLocal() as session:
        repository = AccountsRepository(session)
        account = Account(
            id=account_id,
            chatgpt_account_id=f"chatgpt-{account_id}",
            email=f"{account_id}@example.com",
            plan_type="plus",
            access_token_encrypted=encryptor.encrypt(f"access-{account_id}"),
            refresh_token_encrypted=encryptor.encrypt(f"refresh-{account_id}"),
            id_token_encrypted=encryptor.encrypt(f"id-{account_id}"),
            last_refresh=utcnow(),
            status=AccountStatus.ACTIVE,
            deactivation_reason=None,
        )
        await repository.upsert(account)


def test_automation_presets_unit() -> None:
    presets = list_automation_presets()
    assert len(presets) >= 1
    preset_ids = [p.id for p in presets]
    assert WEEKLY_PRESTART_PRESET_ID in preset_ids

    preset = get_automation_preset(WEEKLY_PRESTART_PRESET_ID)
    assert preset is not None
    assert preset.id == "weekly_prestart"
    assert preset.name == "Weekly Quota Window Prestart"
    assert preset.model == "gpt-5.3-codex-spark"
    assert preset.default_days == ["mon"]
    assert preset.default_time == "00:00"

    assert get_automation_preset("non_existent") is None


@pytest.mark.asyncio
async def test_automations_presets_api(async_client) -> None:
    await _create_test_account("acc-preset-test")

    # 1. List presets
    response = await async_client.get("/api/automations/presets")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(p["id"] == "weekly_prestart" for p in data)

    # 2. Create job from weekly_prestart preset
    create_resp = await async_client.post("/api/automations/presets/weekly_prestart/create")
    assert create_resp.status_code == 200
    job = create_resp.json()
    assert job["name"] == "Weekly Quota Window Prestart"
    assert job["model"] == "gpt-5.3-codex-spark"
    assert job["schedule"]["days"] == ["mon"]
    assert job["schedule"]["time"] == "00:00"
    assert job["schedule"]["timezone"] == "UTC"
    assert job["prompt"] == "Prestart weekly quota window."
    assert job["enabled"] is True

    # 3. Create job from invalid preset returns 404
    err_resp = await async_client.post("/api/automations/presets/unknown_preset/create")
    assert err_resp.status_code == 404
    err_data = err_resp.json()
    assert err_data.get("code") == "preset_not_found" or "preset not found" in str(err_data).lower()
