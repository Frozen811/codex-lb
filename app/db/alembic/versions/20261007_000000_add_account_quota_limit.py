"""Persist per-account quota restrictions."""

import sqlalchemy as sa
from alembic import op

revision = "20261007_000000_add_account_quota_limit"
down_revision = "20260928_020000_add_request_logs_facet_indexes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("accounts", sa.Column("quota_limit_percent", sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column("accounts", "quota_limit_percent")
