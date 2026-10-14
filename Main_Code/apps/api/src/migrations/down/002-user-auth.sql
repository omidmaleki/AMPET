-- AMPET — down برای 002-user-auth (SP-01 / M-01.1)
-- برگشت دقیق: حذف ستون‌های افزوده‌شده + جداول جدید؛ ۵ جدول 001-auth-user دست‌نخورده می‌مانند.
-- توجه: ایندکس‌های ix_sessions_user_revoked و ix_otp_codes_phone_purpose متعلق به 001 هستند و دست نمی‌خورند.

ALTER TABLE sessions DROP COLUMN IF EXISTS updated_at;

DROP INDEX IF EXISTS ix_users_status;
ALTER TABLE users DROP CONSTRAINT IF EXISTS chk_users_status;
ALTER TABLE users
  DROP COLUMN IF EXISTS status,
  DROP COLUMN IF EXISTS last_seen_at,
  DROP COLUMN IF EXISTS terms_version,
  DROP COLUMN IF EXISTS deletion_scheduled_at,
  DROP COLUMN IF EXISTS two_factor_enabled;

DROP TABLE IF EXISTS role_permissions;
DROP TABLE IF EXISTS permissions;
DROP TABLE IF EXISTS terms_acceptances;
