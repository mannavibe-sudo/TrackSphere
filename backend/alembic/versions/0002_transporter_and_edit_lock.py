"""add transporter master and record edit_unlocked flag

Revision ID: 0002
Revises: 0001
Create Date: 2026-08-09

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    entity_status = postgresql.ENUM(
        "active", "inactive", name="entity_status", create_type=False
    )

    op.create_table(
        "transporters",
        sa.Column("transporter_id", postgresql.UUID(as_uuid=True), primary_key=True,
                   server_default=sa.text("uuid_generate_v4()")),
        sa.Column("company_id", postgresql.UUID(as_uuid=True),
                   sa.ForeignKey("companies.company_id", ondelete="CASCADE"), nullable=False),
        sa.Column("transporter_name", sa.String(255), nullable=False),
        sa.Column("status", entity_status, nullable=False, server_default="active"),
        sa.Column("created_date", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("company_id", "transporter_name", name="uq_transporter_per_company"),
    )
    op.create_index("idx_transporters_company_id", "transporters", ["company_id"])

    op.add_column(
        "records",
        sa.Column("edit_unlocked", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )


def downgrade() -> None:
    op.drop_column("records", "edit_unlocked")
    op.drop_table("transporters")
