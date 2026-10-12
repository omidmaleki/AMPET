-- rollback 001_auth_user (SP-00 / M-00.6)
DROP TRIGGER IF EXISTS trg_audit_logs_append_only ON audit_logs;
DROP FUNCTION IF EXISTS audit_logs_block_mutation();
DROP TABLE IF EXISTS audit_logs;
DROP TABLE IF EXISTS sessions;
DROP TABLE IF EXISTS otp_codes;
DROP TABLE IF EXISTS user_roles;
DROP TABLE IF EXISTS users;
DROP FUNCTION IF EXISTS gen_uuid_v7();
-- نکته: افزونه pg_trgm حذف نمی‌شود (SP-12 روی آن می‌سازد).