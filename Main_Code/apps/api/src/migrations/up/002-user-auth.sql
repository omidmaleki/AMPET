-- AMPET — 002-user-auth (SP-01 / M-01.1)
-- ساخته روی 001-auth-user پایه SP-00. جداول جدید + ALTER روی users.

CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- ---------- terms_acceptances ----------
CREATE TABLE terms_acceptances (
  id              uuid PRIMARY KEY DEFAULT gen_uuid_v7(),
  user_id         uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  terms_version   varchar(20) NOT NULL,
  accepted_at     timestamptz NOT NULL DEFAULT now(),
  created_at      timestamptz NOT NULL DEFAULT now(),
  deleted_at      timestamptz
);
CREATE UNIQUE INDEX ux_terms_user_version ON terms_acceptances (user_id, terms_version) WHERE deleted_at IS NULL;

-- ---------- permissions ----------
CREATE TABLE permissions (
  id          uuid PRIMARY KEY DEFAULT gen_uuid_v7(),
  code        varchar(40) NOT NULL UNIQUE,
  name        varchar(100) NOT NULL,
  description text,
  created_at  timestamptz NOT NULL DEFAULT now(),
  deleted_at  timestamptz
);

-- ---------- role_permissions ----------
CREATE TABLE role_permissions (
  id              uuid PRIMARY KEY DEFAULT gen_uuid_v7(),
  role            varchar(40) NOT NULL,
  permission_code varchar(40) NOT NULL REFERENCES permissions(code) ON DELETE CASCADE,
  granted_by      uuid REFERENCES users(id),
  created_at      timestamptz NOT NULL DEFAULT now(),
  deleted_at      timestamptz
);
CREATE UNIQUE INDEX ux_role_perm ON role_permissions (role, permission_code) WHERE deleted_at IS NULL;

-- ---------- ALTER users ----------
ALTER TABLE users
  ADD COLUMN two_factor_enabled boolean NOT NULL DEFAULT false,
  ADD COLUMN deletion_scheduled_at timestamptz,
  ADD COLUMN terms_version varchar(20),
  ADD COLUMN last_seen_at timestamptz,
  ADD COLUMN status varchar(20) NOT NULL DEFAULT 'ACTIVE';

ALTER TABLE users ADD CONSTRAINT chk_users_status CHECK (status IN ('ACTIVE','PENDING_DELETION','SUSPENDED'));
CREATE INDEX ix_users_status ON users (status) WHERE deleted_at IS NULL;

-- ---------- ALTER otp_codes ----------
-- ایندکس (phone, purpose, expires_at) از قبل در 001 به نام ix_otp_codes_phone_purpose هست؛ تکرار نمی‌کنیم.

-- ---------- ALTER sessions ----------
ALTER TABLE sessions ADD COLUMN updated_at timestamptz NOT NULL DEFAULT now();
-- ایندکس (user_id, revoked_at) از قبل در 001 به نام ix_sessions_user_revoked هست؛ تکرار نمی‌کنیم.
