from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock

from sqlalchemy.dialects import mysql
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.accounts.repository import AccountsRepository


async def test_mysql_policy_update_projects_under_lock_without_returning():
    session = AsyncMock(spec=AsyncSession)
    session.get_bind.return_value = SimpleNamespace(dialect=mysql.dialect())
    statements = []

    async def execute(statement, *args, **kwargs):
        statements.append(str(statement.compile(dialect=mysql.dialect())))
        if len(statements) == 1:
            return SimpleNamespace(rowcount=1)
        return SimpleNamespace(
            one_or_none=lambda: SimpleNamespace(
                usage_limit_enabled=True,
                usage_limit_percent=80,
                usage_limit_5h_percent=50,
                usage_limit_weekly_percent=90,
            )
        )

    session.execute.side_effect = execute
    configuration = await AccountsRepository(session).update_usage_limit(
        "synthetic",
        enabled=True,
        percent=80,
        update_percent=True,
        percent_5h=50,
        update_5h=True,
        percent_weekly=90,
        update_weekly=True,
    )
    assert configuration is not None and configuration.percent_5h == 50
    assert statements[0].startswith("UPDATE") and "RETURNING" not in statements[0]
    assert statements[1].endswith("FOR UPDATE")
    session.commit.assert_awaited_once()
