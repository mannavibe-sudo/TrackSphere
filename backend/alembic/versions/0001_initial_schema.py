"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-08-07

Creates the full TrackSphere schema: extensions, enum types, all 8 tables,
indexes, and the two triggers (auto-updated_date, auto status history).
Mirrors database/schema.sql exactly — see that file for the annotated,
human-readable version of this same schema.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ---- Extensions ----
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')

    # ---- Enum types ----
    bind = op.get_bind()

    user_role_create = postgresql.ENUM(
        "super_admin", "company_admin", "data_entry_user", name="user_role"
    )
    record_status_create = postgresql.ENUM(
        "draft", "loading", "dispatched", "in_transit", "delivered",
        "invoice_raised", "payment_received", "closed", name="record_status",
    )
    entity_status_create = postgresql.ENUM("active", "inactive", name="entity_status")
    notification_channel_create = postgresql.ENUM(
        "in_app", "email", "sms", "whatsapp", name="notification_channel"
    )
    user_role_create.create(bind, checkfirst=True)
    record_status_create.create(bind, checkfirst=True)
    entity_status_create.create(bind, checkfirst=True)
    notification_channel_create.create(bind, checkfirst=True)

    # create_type=False: the types above are already created explicitly, so
    # these column-bound instances must not try to CREATE TYPE a second time.
    user_role = postgresql.ENUM(
        "super_admin", "company_admin", "data_entry_user",
        name="user_role", create_type=False,
    )
    record_status = postgresql.ENUM(
        "draft", "loading", "dispatched", "in_transit", "delivered",
        "invoice_raised", "payment_received", "closed",
        name="record_status", create_type=False,
    )
    entity_status = postgresql.ENUM(
        "active", "inactive", name="entity_status", create_type=False
    )
    notification_channel = postgresql.ENUM(
        "in_app", "email", "sms", "whatsapp",
        name="notification_channel", create_type=False,
    )

    # ---- companies ----
    op.create_table(
        "companies",
        sa.Column("company_id", postgresql.UUID(as_uuid=True), primary_key=True,
                   server_default=sa.text("uuid_generate_v4()")),
        sa.Column("company_name", sa.String(255), nullable=False),
        sa.Column("company_code", sa.String(50), nullable=False, unique=True),
        sa.Column("gst_number", sa.String(15)),
        sa.Column("address", sa.Text()),
        sa.Column("contact_person", sa.String(150)),
        sa.Column("contact_number", sa.String(20)),
        sa.Column("email", sa.String(255)),
        sa.Column("status", entity_status, nullable=False, server_default="active"),
        sa.Column("created_date", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_date", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    # ---- users ----
    op.create_table(
        "users",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), primary_key=True,
                   server_default=sa.text("uuid_generate_v4()")),
        sa.Column("company_id", postgresql.UUID(as_uuid=True),
                   sa.ForeignKey("companies.company_id", ondelete="RESTRICT")),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("mobile", sa.String(20)),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", user_role, nullable=False, server_default="data_entry_user"),
        sa.Column("status", entity_status, nullable=False, server_default="active"),
        sa.Column("created_date", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint(
            "(role = 'super_admin' AND company_id IS NULL) OR "
            "(role <> 'super_admin' AND company_id IS NOT NULL)",
            name="chk_super_admin_no_company",
        ),
    )
    op.create_index("idx_users_company_id", "users", ["company_id"])
    op.create_index("idx_users_email", "users", ["email"])

    # ---- records ----
    op.create_table(
        "records",
        sa.Column("record_id", postgresql.UUID(as_uuid=True), primary_key=True,
                   server_default=sa.text("uuid_generate_v4()")),
        sa.Column("company_id", postgresql.UUID(as_uuid=True),
                   sa.ForeignKey("companies.company_id", ondelete="RESTRICT"), nullable=False),
        # Group 1: Loading & Dispatch
        sa.Column("loading_location", sa.String(255)),
        sa.Column("truck_number", sa.String(20)),
        sa.Column("driver_mobile", sa.String(20)),
        sa.Column("weight_at_pi_yard_mt", sa.Numeric(10, 2)),
        sa.Column("eway_bill_no", sa.String(30)),
        sa.Column("date_of_dispatch", sa.Date()),
        sa.Column("lr_no", sa.String(50)),
        sa.Column("delivery_chalan", sa.String(50)),
        sa.Column("cost_of_material", sa.Numeric(12, 2)),
        # Group 2: Transportation
        sa.Column("transporter_name", sa.String(255)),
        sa.Column("transporter_mobile", sa.String(20)),
        sa.Column("capacity_of_truck_mt", sa.Numeric(10, 2)),
        sa.Column("length_of_truck_ft", sa.Numeric(10, 2)),
        sa.Column("rate_fixed_for_transportation", sa.Numeric(12, 2)),
        sa.Column("advance_paid", sa.Numeric(12, 2)),
        sa.Column("advance_payment_date", sa.Date()),
        sa.Column("advance_paid_to", sa.String(255)),
        sa.Column("final_payment", sa.Numeric(12, 2)),
        sa.Column("total_payment_to_transport", sa.Numeric(12, 2)),
        # Group 3: Delivery & Weight at ITC
        sa.Column("truck_entry_date", sa.DateTime(timezone=True)),
        sa.Column("truck_exit_date", sa.DateTime(timezone=True)),
        sa.Column("weight_at_itc_yard_mt", sa.Numeric(10, 2)),
        sa.Column("wc_number", sa.String(50)),
        sa.Column("weight_loss_mt", sa.Numeric(10, 2)),
        # Group 4: Invoice & GST
        sa.Column("invoice_number", sa.String(50)),
        sa.Column("invoice_amount_raised", sa.Numeric(12, 2)),
        sa.Column("amount_raised_date", sa.Date()),
        sa.Column("gst_amount", sa.Numeric(12, 2)),
        sa.Column("payment_received_date", sa.Date()),
        sa.Column("total_amount_received", sa.Numeric(12, 2)),
        sa.Column("margin_pnl", sa.Numeric(12, 2)),
        # System fields
        sa.Column("status", record_status, nullable=False, server_default="draft"),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.user_id")),
        sa.Column("created_date", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_date", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
    )
    op.create_index("idx_records_company_id", "records", ["company_id"])
    op.create_index("idx_records_truck_number", "records", ["truck_number"])
    op.create_index("idx_records_driver_mobile", "records", ["driver_mobile"])
    op.create_index("idx_records_transporter_name", "records", ["transporter_name"])
    op.create_index("idx_records_lr_no", "records", ["lr_no"])
    op.create_index("idx_records_invoice_number", "records", ["invoice_number"])
    op.create_index("idx_records_status", "records", ["status"])
    op.create_index("idx_records_date_of_dispatch", "records", ["date_of_dispatch"])
    op.execute(
        "CREATE INDEX idx_records_deleted_at ON records(deleted_at) WHERE deleted_at IS NULL"
    )
    op.execute("""
        CREATE INDEX idx_records_global_search ON records
            USING gin (
                to_tsvector('simple',
                    coalesce(loading_location,'') || ' ' ||
                    coalesce(truck_number,'')     || ' ' ||
                    coalesce(transporter_name,'') || ' ' ||
                    coalesce(lr_no,'')            || ' ' ||
                    coalesce(invoice_number,'')
                )
            )
    """)

    # ---- record_status_history ----
    op.create_table(
        "record_status_history",
        sa.Column("history_id", postgresql.UUID(as_uuid=True), primary_key=True,
                   server_default=sa.text("uuid_generate_v4()")),
        sa.Column("record_id", postgresql.UUID(as_uuid=True),
                   sa.ForeignKey("records.record_id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", record_status, nullable=False),
        sa.Column("changed_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.user_id")),
        sa.Column("changed_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("remarks", sa.Text()),
    )
    op.create_index("idx_status_history_record_id", "record_status_history", ["record_id"])

    # ---- attachments ----
    op.create_table(
        "attachments",
        sa.Column("attachment_id", postgresql.UUID(as_uuid=True), primary_key=True,
                   server_default=sa.text("uuid_generate_v4()")),
        sa.Column("record_id", postgresql.UUID(as_uuid=True),
                   sa.ForeignKey("records.record_id", ondelete="CASCADE"), nullable=False),
        sa.Column("file_name", sa.String(255), nullable=False),
        sa.Column("file_url", sa.Text(), nullable=False),
        sa.Column("file_type", sa.String(50)),
        sa.Column("uploaded_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.user_id")),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("idx_attachments_record_id", "attachments", ["record_id"])

    # ---- comments ----
    op.create_table(
        "comments",
        sa.Column("comment_id", postgresql.UUID(as_uuid=True), primary_key=True,
                   server_default=sa.text("uuid_generate_v4()")),
        sa.Column("record_id", postgresql.UUID(as_uuid=True),
                   sa.ForeignKey("records.record_id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                   sa.ForeignKey("users.user_id"), nullable=False),
        sa.Column("comment_text", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("idx_comments_record_id", "comments", ["record_id"])

    # ---- audit_logs ----
    op.create_table(
        "audit_logs",
        sa.Column("audit_id", postgresql.UUID(as_uuid=True), primary_key=True,
                   server_default=sa.text("uuid_generate_v4()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.user_id")),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("companies.company_id")),
        sa.Column("action", sa.String(20), nullable=False),
        sa.Column("entity_type", sa.String(50), nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True)),
        sa.Column("old_value", postgresql.JSONB()),
        sa.Column("new_value", postgresql.JSONB()),
        sa.Column("ip_address", postgresql.INET()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("idx_audit_logs_company_id", "audit_logs", ["company_id"])
    op.create_index("idx_audit_logs_entity", "audit_logs", ["entity_type", "entity_id"])
    op.create_index("idx_audit_logs_created_at", "audit_logs", ["created_at"])

    # ---- notifications ----
    op.create_table(
        "notifications",
        sa.Column("notification_id", postgresql.UUID(as_uuid=True), primary_key=True,
                   server_default=sa.text("uuid_generate_v4()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                   sa.ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False),
        sa.Column("channel", notification_channel, nullable=False, server_default="in_app"),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("message", sa.Text()),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("idx_notifications_user_id", "notifications", ["user_id", "is_read"])

    # ---- Trigger functions ----
    op.execute("""
        CREATE OR REPLACE FUNCTION set_updated_timestamp()
        RETURNS TRIGGER AS $$
        BEGIN
            IF TG_TABLE_NAME = 'records' THEN
                NEW.updated_date := now();
            ELSIF TG_TABLE_NAME = 'companies' THEN
                NEW.updated_date := now();
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    op.execute("""
        CREATE TRIGGER trg_companies_updated
            BEFORE UPDATE ON companies
            FOR EACH ROW EXECUTE FUNCTION set_updated_timestamp();
    """)
    op.execute("""
        CREATE TRIGGER trg_records_updated
            BEFORE UPDATE ON records
            FOR EACH ROW EXECUTE FUNCTION set_updated_timestamp();
    """)
    op.execute("""
        CREATE OR REPLACE FUNCTION log_record_status_change()
        RETURNS TRIGGER AS $$
        BEGIN
            IF (TG_OP = 'INSERT') OR (OLD.status IS DISTINCT FROM NEW.status) THEN
                INSERT INTO record_status_history (record_id, status, changed_by)
                VALUES (NEW.record_id, NEW.status, NEW.created_by);
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    op.execute("""
        CREATE TRIGGER trg_record_status_history
            AFTER INSERT OR UPDATE ON records
            FOR EACH ROW EXECUTE FUNCTION log_record_status_change();
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_record_status_history ON records")
    op.execute("DROP FUNCTION IF EXISTS log_record_status_change()")
    op.execute("DROP TRIGGER IF EXISTS trg_records_updated ON records")
    op.execute("DROP TRIGGER IF EXISTS trg_companies_updated ON companies")
    op.execute("DROP FUNCTION IF EXISTS set_updated_timestamp()")

    op.drop_table("notifications")
    op.drop_table("audit_logs")
    op.drop_table("comments")
    op.drop_table("attachments")
    op.drop_table("record_status_history")
    op.drop_table("records")
    op.drop_table("users")
    op.drop_table("companies")

    postgresql.ENUM(name="notification_channel").drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name="entity_status").drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name="record_status").drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name="user_role").drop(op.get_bind(), checkfirst=True)
