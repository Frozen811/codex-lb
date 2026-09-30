from __future__ import annotations

import uuid
from typing import cast

from sqlalchemy import Enum as SqlEnum

from app.db.models import Account, AccountStatus, ApiKeyLimit, LimitType, LimitWindow, new_codex_installation_id


def test_sqlalchemy_enums_use_string_values() -> None:
    account_status_type = cast(SqlEnum, Account.__table__.c.status.type)
    limit_type_type = cast(SqlEnum, ApiKeyLimit.__table__.c.limit_type.type)
    limit_window_type = cast(SqlEnum, ApiKeyLimit.__table__.c.limit_window.type)

    assert account_status_type.enums == [status.value for status in AccountStatus]
    assert limit_type_type.enums == [limit_type.value for limit_type in LimitType]
    assert limit_window_type.enums == [window.value for window in LimitWindow]


def test_account_codex_installation_id_has_uuid_default() -> None:
    column = Account.__table__.c.codex_installation_id
    default = column.default

    assert column.nullable is False
    assert default is not None
    assert callable(default.arg)
    generated = new_codex_installation_id()
    assert isinstance(generated, str)
    assert str(uuid.UUID(generated)) == generated


def test_mysql_type_sizing_does_not_pollute_sqlite_ddl() -> None:
    from unittest.mock import MagicMock

    from sqlalchemy import create_engine
    from sqlalchemy.dialects import mysql, sqlite
    from sqlalchemy.schema import CreateTable

    from app.db.models import Base
    from app.db.mysql_compat import _size_strings_for_mysql

    mock_conn = MagicMock()
    mock_conn.dialect.name = "mysql"

    for table in Base.metadata.tables.values():
        _size_strings_for_mysql(table, mock_conn)

    # SQLite must successfully create all tables without 'no such collation sequence: utf8mb4_bin'
    sqlite_engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(sqlite_engine)

    # Sentinel columns must keep utf8mb4_bin on MySQL while omitting it on SQLite
    rollups_table = Base.metadata.tables["request_usage_hourly_rollups"]
    mysql_ddl = str(CreateTable(rollups_table).compile(dialect=mysql.dialect()))
    sqlite_ddl = str(CreateTable(rollups_table).compile(dialect=sqlite.dialect()))

    assert "utf8mb4_bin" in mysql_ddl
    assert "utf8mb4_bin" not in sqlite_ddl
