"""Add opt-in durable source catalogs on the current fork lineage."""

import sqlalchemy as sa
from alembic import op

revision = "20261010_000000_add_source_catalog_discovery"
down_revision = "20261009_010000_add_account_window_reserves"
branch_labels = None
depends_on = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    columns = {column["name"] for column in inspector.get_columns("model_sources")}
    for column in (
        sa.Column("catalog_mode", sa.String(32), nullable=False, server_default="manual"),
        sa.Column("catalog_revision", sa.Integer(), nullable=False, server_default="0"),
    ):
        if column.name not in columns:
            op.add_column("model_sources", column)
    model_columns = {column["name"] for column in inspector.get_columns("model_source_models")}
    if "is_available" not in model_columns:
        op.add_column(
            "model_source_models", sa.Column("is_available", sa.Boolean(), nullable=False, server_default=sa.true())
        )


def downgrade() -> None:
    with op.batch_alter_table("model_source_models") as batch:
        batch.drop_column("is_available")
    with op.batch_alter_table("model_sources") as batch:
        batch.drop_column("catalog_revision")
        batch.drop_column("catalog_mode")
