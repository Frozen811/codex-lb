"""Add opt-in sticky reallocation timing with compatible historical defaults."""

import sqlalchemy as sa
from alembic import op

revision = "20261014_000000_add_sticky_reallocation_timing"
down_revision = "20261010_000000_add_source_catalog_discovery"
branch_labels = None
depends_on = None


def upgrade() -> None:
    columns = {column["name"] for column in sa.inspect(op.get_bind()).get_columns("dashboard_settings")}
    if "sticky_reallocation_timing" not in columns:
        op.add_column(
            "dashboard_settings",
            sa.Column("sticky_reallocation_timing", sa.String(32), nullable=False, server_default="immediate"),
        )


def downgrade() -> None:
    with op.batch_alter_table("dashboard_settings") as batch:
        batch.drop_column("sticky_reallocation_timing")
