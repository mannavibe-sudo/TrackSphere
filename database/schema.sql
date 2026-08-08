-- ============================================================================
-- TrackSphere — PostgreSQL Database Schema
-- Module 3: Database Design
-- ============================================================================
-- Multi-tenant strategy: shared database, shared schema, row-level isolation
-- via company_id on every business table. Super Admin (role='super_admin')
-- bypasses the company_id filter at the service layer; every other role is
-- always scoped to their own company_id.
-- ============================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================================
-- ENUM TYPES
-- ============================================================================

CREATE TYPE user_role AS ENUM ('super_admin', 'company_admin', 'data_entry_user');

CREATE TYPE record_status AS ENUM (
    'draft',
    'loading',
    'dispatched',
    'in_transit',
    'delivered',
    'invoice_raised',
    'payment_received',
    'closed'
);

CREATE TYPE entity_status AS ENUM ('active', 'inactive');

CREATE TYPE notification_channel AS ENUM ('in_app', 'email', 'sms', 'whatsapp');

-- ============================================================================
-- TABLE: companies
-- Company Master. Super Admin creates/manages these. Also bulk-manageable
-- via Excel Import/Export (see API module) so new companies can be added
-- without touching the UI.
-- ============================================================================

CREATE TABLE companies (
    company_id       UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_name     VARCHAR(255) NOT NULL,
    company_code     VARCHAR(50)  NOT NULL UNIQUE,
    gst_number       VARCHAR(15),
    address          TEXT,
    contact_person   VARCHAR(150),
    contact_number   VARCHAR(20),
    email            VARCHAR(255),
    status           entity_status NOT NULL DEFAULT 'active',
    created_date     TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_date     TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE companies IS 'Company Master — every tenant on the platform.';

-- ============================================================================
-- TABLE: users
-- ============================================================================

CREATE TABLE users (
    user_id        UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id     UUID REFERENCES companies(company_id) ON DELETE RESTRICT,
    -- company_id is NULL only for super_admin, who is not tied to one company
    name           VARCHAR(150) NOT NULL,
    email          VARCHAR(255) NOT NULL UNIQUE,
    mobile         VARCHAR(20),
    password_hash  VARCHAR(255) NOT NULL,
    role           user_role NOT NULL DEFAULT 'data_entry_user',
    status         entity_status NOT NULL DEFAULT 'active',
    created_date   TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT chk_super_admin_no_company
        CHECK (
            (role = 'super_admin' AND company_id IS NULL)
            OR (role <> 'super_admin' AND company_id IS NOT NULL)
        )
);

CREATE INDEX idx_users_company_id ON users(company_id);
CREATE INDEX idx_users_email ON users(email);

-- ============================================================================
-- TABLE: records
-- Generated exactly from the uploaded Excel (Sheet1, 31 fields, 4 groups:
-- Loading & Dispatch / Transportation / Delivery & Weight at ITC /
-- Invoice & GST). Column names below map 1:1 to Excel headers — see the
-- mapping table in docs/excel-field-mapping.md. No field renamed, merged,
-- or removed.
-- ============================================================================

CREATE TABLE records (
    record_id        UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id        UUID NOT NULL REFERENCES companies(company_id) ON DELETE RESTRICT,

    -- ---- Group 1: Loading & Dispatch ----
    loading_location          VARCHAR(255),
    truck_number               VARCHAR(20),
    driver_mobile               VARCHAR(20),
    weight_at_pi_yard_mt      NUMERIC(10,2),
    eway_bill_no               VARCHAR(30),
    date_of_dispatch           DATE,
    lr_no                      VARCHAR(50),
    delivery_chalan            VARCHAR(50),
    cost_of_material            NUMERIC(12,2),

    -- ---- Group 2: Transportation ----
    transporter_name            VARCHAR(255),
    transporter_mobile          VARCHAR(20),
    capacity_of_truck_mt        NUMERIC(10,2),
    length_of_truck_ft          NUMERIC(10,2),
    rate_fixed_for_transportation NUMERIC(12,2),
    advance_paid                NUMERIC(12,2),
    advance_payment_date        DATE,
    advance_paid_to             VARCHAR(255),
    final_payment                NUMERIC(12,2),
    total_payment_to_transport  NUMERIC(12,2),

    -- ---- Group 3: Delivery & Weight at ITC ----
    truck_entry_date            TIMESTAMPTZ,
    truck_exit_date              TIMESTAMPTZ,
    weight_at_itc_yard_mt       NUMERIC(10,2),
    wc_number                   VARCHAR(50),
    weight_loss_mt               NUMERIC(10,2),

    -- ---- Group 4: Invoice & GST ----
    invoice_number               VARCHAR(50),
    invoice_amount_raised        NUMERIC(12,2),
    amount_raised_date           DATE,
    gst_amount                   NUMERIC(12,2),
    payment_received_date        DATE,
    total_amount_received        NUMERIC(12,2),
    margin_pnl                   NUMERIC(12,2),

    -- ---- System / tracking fields (brief requirement, not from Excel) ----
    status            record_status NOT NULL DEFAULT 'draft',
    created_by         UUID REFERENCES users(user_id),
    created_date       TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_date       TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at          TIMESTAMPTZ  -- soft delete; NULL = not deleted
);

COMMENT ON TABLE records IS 'Core transport/tracking record. Field set generated verbatim from uploaded Excel.';
COMMENT ON COLUMN records.weight_loss_mt IS 'Weight at PI Yard minus Weight at ITC Yard, typically. Stored, not computed on read, so historic reports stay stable.';

-- Indexes matching the brief's required Search & Filters fields
CREATE INDEX idx_records_company_id       ON records(company_id);
CREATE INDEX idx_records_truck_number     ON records(truck_number);
CREATE INDEX idx_records_driver_mobile    ON records(driver_mobile);
CREATE INDEX idx_records_transporter_name ON records(transporter_name);
CREATE INDEX idx_records_lr_no            ON records(lr_no);
CREATE INDEX idx_records_invoice_number   ON records(invoice_number);
CREATE INDEX idx_records_status           ON records(status);
CREATE INDEX idx_records_date_of_dispatch ON records(date_of_dispatch);
CREATE INDEX idx_records_deleted_at       ON records(deleted_at) WHERE deleted_at IS NULL;

-- Global search support (loading location, truck, transporter, LR, invoice)
CREATE INDEX idx_records_global_search ON records
    USING gin (
        to_tsvector('simple',
            coalesce(loading_location,'') || ' ' ||
            coalesce(truck_number,'')     || ' ' ||
            coalesce(transporter_name,'') || ' ' ||
            coalesce(lr_no,'')            || ' ' ||
            coalesce(invoice_number,'')
        )
    );

-- ============================================================================
-- TABLE: record_status_history
-- Complete lifecycle tracking (Draft -> ... -> Closed), one row per transition.
-- ============================================================================

CREATE TABLE record_status_history (
    history_id    UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    record_id      UUID NOT NULL REFERENCES records(record_id) ON DELETE CASCADE,
    status         record_status NOT NULL,
    changed_by     UUID REFERENCES users(user_id),
    changed_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    remarks        TEXT
);

CREATE INDEX idx_status_history_record_id ON record_status_history(record_id);

-- ============================================================================
-- TABLE: attachments
-- ============================================================================

CREATE TABLE attachments (
    attachment_id  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    record_id       UUID NOT NULL REFERENCES records(record_id) ON DELETE CASCADE,
    file_name       VARCHAR(255) NOT NULL,
    file_url        TEXT NOT NULL,
    file_type       VARCHAR(50),
    uploaded_by     UUID REFERENCES users(user_id),
    uploaded_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_attachments_record_id ON attachments(record_id);

-- ============================================================================
-- TABLE: comments
-- ============================================================================

CREATE TABLE comments (
    comment_id     UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    record_id       UUID NOT NULL REFERENCES records(record_id) ON DELETE CASCADE,
    user_id         UUID NOT NULL REFERENCES users(user_id),
    comment_text    TEXT NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_comments_record_id ON comments(record_id);

-- ============================================================================
-- TABLE: audit_logs
-- Generic across every entity type (company, user, record) so Super Admin
-- has one place to see all system activity.
-- ============================================================================

CREATE TABLE audit_logs (
    audit_id       UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID REFERENCES users(user_id),
    company_id      UUID REFERENCES companies(company_id),
    action          VARCHAR(20) NOT NULL,   -- CREATE / UPDATE / DELETE / LOGIN / etc.
    entity_type     VARCHAR(50) NOT NULL,   -- 'company' | 'user' | 'record' | ...
    entity_id       UUID,
    old_value        JSONB,
    new_value        JSONB,
    ip_address       INET,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_audit_logs_company_id  ON audit_logs(company_id);
CREATE INDEX idx_audit_logs_entity      ON audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_logs_created_at  ON audit_logs(created_at);

-- ============================================================================
-- TABLE: notifications
-- Channel-agnostic from day one: in_app now, email/sms/whatsapp later just
-- add rows with a different channel value — no schema change needed.
-- ============================================================================

CREATE TABLE notifications (
    notification_id  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id           UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    channel           notification_channel NOT NULL DEFAULT 'in_app',
    type              VARCHAR(50) NOT NULL,   -- 'record_status_change', 'payment_due', ...
    title              VARCHAR(255) NOT NULL,
    message            TEXT,
    is_read            BOOLEAN NOT NULL DEFAULT false,
    created_at         TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_notifications_user_id ON notifications(user_id, is_read);

-- ============================================================================
-- TRIGGERS: auto-update updated_date / updated_at columns
-- ============================================================================

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

CREATE TRIGGER trg_companies_updated
    BEFORE UPDATE ON companies
    FOR EACH ROW EXECUTE FUNCTION set_updated_timestamp();

CREATE TRIGGER trg_records_updated
    BEFORE UPDATE ON records
    FOR EACH ROW EXECUTE FUNCTION set_updated_timestamp();

-- ============================================================================
-- TRIGGER: auto-log status changes into record_status_history
-- ============================================================================

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

CREATE TRIGGER trg_record_status_history
    AFTER INSERT OR UPDATE ON records
    FOR EACH ROW EXECUTE FUNCTION log_record_status_change();

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================
