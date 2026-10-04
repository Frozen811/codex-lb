from __future__ import annotations

import json

import aiohttp
import pytest
from aiohttp import web
from aiohttp.test_utils import TestServer
from aiohttp_retry import RetryClient
from sqlalchemy import select

from app.core.clients import proxy as core_proxy
from app.core.clients import usage as usage_client
from app.core.plan_types import account_plan_matches_allowed, normalize_rate_limit_plan_type
from app.core.usage import capacity_for_plan
from app.db.models import Account, UsageHistory
from app.db.session import SessionLocal
from app.modules.accounts.repository import AccountsRepository
from app.modules.proxy import service as proxy_service
from app.modules.usage.repository import UsageRepository
from app.modules.usage.updater import UsageUpdater
from tests.integration.test_proxy_chat_completions import _encode_jwt, _make_auth_json

pytestmark = pytest.mark.integration


async def _import_plan(client, plan: str) -> str:
    auth = _make_auth_json("plan-json-owner", "plan-json@example.invalid")
    auth["tokens"]["idToken"] = _encode_jwt(
        {
            "email": "plan-json@example.invalid",
            "chatgpt_account_id": "plan-json-owner",
            "https://api.openai.com/auth": {"chatgpt_plan_type": plan},
        }
    )
    response = await client.post(
        "/api/accounts/import", files={"auth_json": ("auth.json", json.dumps(auth), "application/json")}
    )
    assert response.status_code == 200, response.text
    return response.json()["accountId"]


@pytest.mark.asyncio
@pytest.mark.parametrize("plan", ["self_serve_business_prolite", " SELF_SERVE_BUSINESS_PROLITE ", "prolite"])
async def test_imported_business_prolite_has_canonical_dashboard_plan(async_client, plan):
    owner = await _import_plan(async_client, plan)
    async with SessionLocal() as database:
        account = await database.get(Account, owner)
        assert account is not None and account.plan_type == "prolite"
        assert account.chatgpt_account_id == "plan-json-owner"
        assert account.workspace_id is None
    response = await async_client.get("/api/accounts")
    assert response.status_code == 200
    row = next(row for row in response.json()["accounts"] if row["accountId"] == owner)
    assert row["planType"] == "prolite"
    assert capacity_for_plan(plan, "primary") == 1125.0
    assert capacity_for_plan(plan, "secondary") == 37800.0
    assert normalize_rate_limit_plan_type(plan) == "prolite"
    assert account_plan_matches_allowed(plan, frozenset({"pro"}))
    assert not account_plan_matches_allowed(plan, frozenset({"plus"}))


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("plan", "workspace", "accepted"),
    [
        ("self_serve_business_prolite", None, True),
        (" SELF_SERVE_BUSINESS_PROLITE ", None, True),
        ("prolite", None, True),
        ("future_plan", None, False),
        ("self_serve_business_prolite", "different-workspace", False),
    ],
)
async def test_business_prolite_refresh_persists_usage_without_identity_drift(
    async_client, monkeypatch, plan, workspace, accepted
):
    owner = await _import_plan(async_client, "team")
    async with SessionLocal() as database:
        account = await database.get(Account, owner)
        assert account is not None
        if workspace is not None:
            account.workspace_id = "owned-workspace"
            await database.commit()
        original_workspace = account.workspace_id
        credentials = (account.access_token_encrypted, account.refresh_token_encrypted, account.id_token_encrypted)

    observed = []

    async def upstream(request):
        observed.append((request.headers.get("ChatGPT-Account-Id"), request.headers.get("Authorization")))
        payload = {
            "plan_type": plan,
            "rate_limit": {
                "primary_window": {"used_percent": 10, "limit_window_seconds": 18000},
                "secondary_window": {"used_percent": 20, "limit_window_seconds": 604800},
            },
        }
        if workspace is not None:
            payload["workspace_id"] = workspace
        return web.json_response(payload)

    application = web.Application()
    application.router.add_get("/{tail:.*}", upstream)
    async with TestServer(application) as server, RetryClient() as client:

        async def fetch_local(**kwargs):
            kwargs.pop("route", None)
            kwargs.pop("allow_direct_egress", None)
            return await usage_client.fetch_usage(
                **kwargs, base_url=str(server.make_url("/")), client=client, max_retries=0, allow_direct_egress=True
            )

        monkeypatch.setattr("app.modules.usage.updater.fetch_usage", fetch_local)
        async with SessionLocal() as database:
            account = await database.get(Account, owner)
            updater = UsageUpdater(UsageRepository(database), accounts_repo=AccountsRepository(database))
            assert await updater.force_refresh(account) is accepted

    assert observed == [("plan-json-owner", "Bearer access-token")]
    async with SessionLocal() as database:
        account = await database.get(Account, owner)
        rows = list((await database.scalars(select(UsageHistory).where(UsageHistory.account_id == owner))).all())
        assert account.plan_type == ("prolite" if accepted else "team")
        assert account.chatgpt_account_id == "plan-json-owner" and account.workspace_id == original_workspace
        assert (
            account.access_token_encrypted,
            account.refresh_token_encrypted,
            account.id_token_encrypted,
        ) == credentials
        assert [(row.window, row.used_percent) for row in sorted(rows, key=lambda row: row.window)] == (
            [("primary", 10.0), ("secondary", 20.0)] if accepted else []
        )
    if accepted:
        summary = await async_client.get("/api/usage/summary")
        assert summary.status_code == 200
        assert summary.json()["primaryWindow"]["capacityCredits"] == 1125.0
        assert summary.json()["secondaryWindow"]["capacityCredits"] == 37800.0


@pytest.mark.asyncio
@pytest.mark.parametrize("format_control", ["object", "string", "text"])
@pytest.mark.parametrize("role", ["system", "developer"])
@pytest.mark.parametrize("parts", [False, True])
@pytest.mark.parametrize("stream", [False, True])
@pytest.mark.parametrize("path", ["/v1/chat/completions", "/v1/chat/completions/"])
async def test_chat_json_mode_keeps_instruction_on_actual_upstream_wire(
    async_client, monkeypatch, format_control, role, parts, stream, path
):
    await _import_plan(async_client, "plus")
    json_instruction = "Return JsOn only. Привет\r\nPreserve order."
    content = [{"type": "text", "text": json_instruction}] if parts else json_instruction
    messages = [
        {"role": "system", "content": "Be brief."},
        {"role": "user", "content": "Earlier question"},
        {"role": role, "content": content},
        {"role": "developer", "content": "Use exact keys."},
        {"role": "user", "content": "Answer now"},
    ]
    controls = (
        {"text": {"format": {"type": "json_object"}}}
        if format_control == "text"
        else {"response_format": {"type": "json_object"} if format_control == "object" else "json_object"}
    )
    observed = []

    async def upstream(request):
        wire = await request.json()
        observed.append(wire)
        assert wire["instructions"] == "Be brief.\nUse exact keys."
        assert wire["text"]["format"] == {"type": "json_object"}
        assert wire["input"][1] == {"role": "developer", "content": [{"type": "input_text", "text": json_instruction}]}
        assert [item["role"] for item in wire["input"]] == ["user", "developer", "user"] + (
            ["user"] if len(observed) == 2 else []
        )
        output = '{"ok":true}'
        frames = [
            {"type": "response.output_text.delta", "delta": output},
            {
                "type": "response.completed",
                "response": {
                    "id": f"resp_json_{len(observed)}",
                    "status": "completed",
                    "model": "gpt-5.2",
                    "output": [
                        {"type": "message", "role": "assistant", "content": [{"type": "output_text", "text": output}]}
                    ],
                    "usage": {"input_tokens": 10, "output_tokens": 5},
                },
            },
        ]
        return web.Response(
            text="".join(f"data: {json.dumps(frame)}\n\n" for frame in frames), content_type="text/event-stream"
        )

    application = web.Application()
    application.router.add_post("/codex/responses", upstream)
    monkeypatch.setattr(core_proxy, "discover_native_egress_client", lambda: None)
    async with TestServer(application) as server, aiohttp.ClientSession() as session:

        async def stream_local(payload, headers, access_token, account_id, **kwargs):
            async for block in core_proxy.stream_responses(
                payload,
                headers,
                access_token,
                account_id,
                base_url=str(server.make_url("/")),
                session=session,
                upstream_stream_transport_override="http",
            ):
                yield block

        monkeypatch.setattr(proxy_service, "core_stream_responses", stream_local)
        for turn in range(2):
            response = await async_client.post(
                path,
                json={"model": "gpt-5.2", "messages": messages, "stream": stream, **controls},
                follow_redirects=True,
            )
            assert response.status_code == 200, response.text
            if stream:
                assert "[DONE]" in response.text and '"ok"' in response.text.replace('\\"', '"')
                assert '"error"' not in response.text
            else:
                assert json.loads(response.json()["choices"][0]["message"]["content"]) == {"ok": True}
            messages = [*messages, {"role": "user", "content": "Follow-up without the format word"}]
    assert len(observed) == 2
    assert observed[1]["input"][:3] == observed[0]["input"]
