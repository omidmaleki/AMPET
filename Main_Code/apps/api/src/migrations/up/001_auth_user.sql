-- AMPET — 001_auth_user (SP-00 / M-00.6)
-- گروه ERD ۱: Auth/User → جداول users, user_roles, otp_codes, sessions, audit_logs
-- قواعد: id UUIDv7، money NUMERIC(18,0) (اینجا)، created_at/updated_at ISO، soft-delete با deleted_at،
--        audit_logs فقط‌افزودنی (امنیت §۸ سناریو ۴).

CREATE EXTENSION IF NOT EXISTS pg_trgm;   -- برای جستجوی فاز بعدی (SP-12)

-- ---------- UUIDv7 ----------
CREATE OR REPLACE FUNCTION gen_uuid_v7() RETURNS uuid
LANGUAGE plpgsql VOLATILE AS $$
DECLARE
  ts_hex text;
  rand_a text;
  rand_b text;
BEGIN
  ts_hex := lpad(to_hex((extract(epoch from clock_timestamp()) * 1000)::bigint), 12, '0');
  rand_a := lpad(to_hex(floor(random() * 4096)::int), 3, '0');                     -- ۱۲ بیت
  rand_b := lpad(to_hex(floor(random() * (1::bigint << 62))::bigint), 16, '0');    -- ۶۲ بیت
  RETURN (ts_hex || '7' || rand_a || rand_b)::uuid;
END;
$$;

-- ---------- users ----------
CREATE TABLE users (
  id         uuid PRIMARY KEY DEFAULT gen_uuid_v7(),
  phone      varchar(15)  NOT NULL,
  full_name  varchar(100),
  is_active  boolean      NOT NULL DEFAULT true,
  created_at timestamptz  NOT NULL DEFAULT now(),
  updated_at timestamptz  NOT NULL DEFAULT now(),
  deleted_at timestamptz
);
CREATE UNIQUE INDEX ux_users_phone_active ON users (phone) WHERE deleted_at IS NULL;

-- ---------- user_roles ----------
CREATE TABLE user_roles (
  id         uuid PRIMARY KEY DEFAULT gen_uuid_v7(),
  user_id    uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  role       varchar(40) NOT NULL,
  granted_by uuid REFERENCES users(id),
  created_at timestamptz NOT NULL DEFAULT now(),
  deleted_at timestamptz
);
CREATE UNIQUE INDEX ux_user_roles_user_role ON user_roles (user_id, role) WHERE deleted_at IS NULL;

-- ---------- otp_codes ----------
CREATE TABLE otp_codes (
  id           uuid PRIMARY KEY DEFAULT gen_uuid_v7(),
  phone        varchar(15) NOT NULL,
  purpose      varchar(20) NOT NULL DEFAULT 'login',
  code_hash    varchar(128) NOT NULL,
  attempts     smallint    NOT NULL DEFAULT 0,
  expires_at   timestamptz NOT NULL,
  locked_until timestamptz,
  created_at   timestamptz NOT NULL DEFAULT now(),
  deleted_at   timestamptz
);
CREATE INDEX ix_otp_codes_phone_purpose ON otp_codes (phone, purpose, expires_at);

-- ---------- sessions ----------
CREATE TABLE sessions (
  id           uuid PRIMARY KEY DEFAULT gen_uuid_v7(),
  user_id      uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  refresh_hash varchar(128) NOT NULL,
  device_id    varchar(128),
  platform     varchar(20),
  user_agent   varchar(300),
  ip           inet,
  expires_at   timestamptz NOT NULL,
  revoked_at   timestamptz,
  created_at   timestamptz NOT NULL DEFAULT now(),
  deleted_at   timestamptz
);
CREATE INDEX ix_sessions_user_revoked ON sessions (user_id, revoked_at);

-- ---------- audit_logs (فقط‌افزودنی) ----------
CREATE TABLE audit_logs (
  id          uuid PRIMARY KEY DEFAULT gen_uuid_v7(),
  actor_id    uuid REFERENCES users(id),
  action      varchar(80) NOT NULL,
  entity_type varchar(80) NOT NULL,
  entity_id   varchar(80),
  before_data jsonb,
  after_data  jsonb,
  ip          inet,
  request_id  varchar(64),
  created_at  timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX ix_audit_logs_entity ON audit_logs (entity_type, entity_id);
CREATE INDEX ix_audit_logs_created ON audit_logs (created_at);

CREATE OR REPLACE FUNCTION audit_logs_block_mutation() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
  RAISE EXCEPTION 'audit_logs فقط‌افزودنی است: ویرایش/حذف ممنوع';
END;
$$;

CREATE TRIGGER trg_audit_logs_append_only
  BEFORE UPDATE OR DELETE ON audit_logs
  FOR EACH ROW EXECUTE FUNCTION audit_logs_block_mutation();