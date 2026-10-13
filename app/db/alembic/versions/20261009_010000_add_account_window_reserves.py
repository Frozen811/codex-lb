"""Add account reserve policy on the fork's current linear lineage."""

import sqlalchemy as sa
from alembic import op

revision = "20261009_010000_add_account_window_reserves"
down_revision = "20261009_000000_activate_reset_warmup_threshold"
branch_labels = None
depends_on = None

_PERCENTS = ("usage_limit_percent", "usage_limit_5h_percent", "usage_limit_weekly_percent")
_REQUIRES = "ck_accounts_usage_limit_enabled_requires_percent"


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    columns = {column["name"] for column in inspector.get_columns("accounts")}
    constraints = {constraint["name"] for constraint in inspector.get_check_constraints("accounts")}
    adding_policy = "usage_limit_enabled" not in columns
    with op.batch_alter_table("accounts") as batch:
        if adding_policy:
            batch.add_column(sa.Column("usage_limit_enabled", sa.Boolean(), nullable=False, server_default=sa.false()))
        for name in _PERCENTS:
            if name not in columns:
                batch.add_column(sa.Column(name, sa.Float(), nullable=True))
            constraint = f"ck_accounts_{name}_range"
            if constraint not in constraints:
                batch.create_check_constraint(constraint, f"{name} IS NULL OR ({name} > 0 AND {name} <= 100)")
        if _REQUIRES not in constraints:
            batch.create_check_constraint(
                _REQUIRES,
                "NOT usage_limit_enabled OR usage_limit_percent IS NOT NULL "
                "OR usage_limit_5h_percent IS NOT NULL OR usage_limit_weekly_percent IS NOT NULL",
            )
    if adding_policy:
        op.execute(
            sa.text(
                "UPDATE accounts SET usage_limit_enabled=true, usage_limit_percent=quota_limit_percent "
                "WHERE quota_limit_percent > 0 AND quota_limit_percent <= 100"
            )
        )


def downgrade() -> None:
    with op.batch_alter_table("accounts") as batch:
        batch.drop_constraint(_REQUIRES, type_="check")
        for name in _PERCENTS:
            batch.drop_constraint(f"ck_accounts_{name}_range", type_="check")
            batch.drop_column(name)
        batch.drop_column("usage_limit_enabled")
