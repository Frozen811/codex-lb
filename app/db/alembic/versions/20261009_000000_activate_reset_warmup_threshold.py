"""Activate the reset warm-up floor without rewriting the legacy setting."""

import sqlalchemy as sa
from alembic import op

revision = "20261009_000000_activate_reset_warmup_threshold"
down_revision = "20261007_000000_add_account_quota_limit"
branch_labels = None
depends_on = None


def upgrade() -> None:
    for column in sa.inspect(op.get_bind()).get_columns("dashboard_settings"):
        if column["name"] != "limit_warmup_reset_threshold_percent":
            continue
        default = str(column["default"]).partition("::")[0].strip("() '\"")
        if column["nullable"] or not isinstance(column["type"], sa.Float) or default not in {"0", "0.0"}:
            raise RuntimeError("Existing reset warm-up threshold column has an incompatible schema")
        # A rewound migration ledger must retain the operator's active value.
        return
    op.add_column(
        "dashboard_settings",
        sa.Column("limit_warmup_reset_threshold_percent", sa.Float(), nullable=False, server_default=sa.text("0.0")),
    )


def downgrade() -> None:
    op.drop_column("dashboard_settings", "limit_warmup_reset_threshold_percent")
