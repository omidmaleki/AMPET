-- SP-01 M-01.1 — seed مجوزها + ماتریس نقش↔مجوز + ادمین اولیه (از .env)
-- فقط در staging/dev. اجرا: npm run db:seed  (یا psql -f)
-- ماتریس پایه از project-document.md:1342-1366؛ در SP-01 فقط زیرمجموعه Auth/User.
-- «پیک» عمداً نقش نیست (project-document.md:1334).

-- ---------- permissions ----------
INSERT INTO permissions (code, name, description) VALUES
('user:me_read', 'پروفایل', 'مشاهده پروفایل خود'),
('user:me_patch', 'ویرایش پروفایل', 'ویرایش نام/اطلاعات پایه'),
('user:sessions_read', 'نشست‌ها', 'لیست نشست‌های فعال'),
('user:sessions_revoke', 'ابطال نشست', 'باطل کردن یک/همه نشست‌ها'),
('admin:users_read', 'لیست کاربران', 'مشاهده کاربران'),
('admin:users_role_patch', 'تغییر نقش', 'تغییر نقش کاربر'),
('admin:audit_read', 'لاگ', 'مشاهده audit_logs'),
('admin:2fa_verify', 'تأیید 2FA', 'تأیید کد ادمین مالی/Super')
ON CONFLICT (code) DO NOTHING;

-- ---------- role_permissions (ماتریس SP-01) ----------
-- مشتری/فروشنده/ارائه‌دهنده/مدیرمحتوای سلامت → فقط قابلیت‌های کاربر عادی
INSERT INTO role_permissions (role, permission_code)
SELECT r.role, p.code
FROM (VALUES
  ('customer'), ('seller'), ('provider'), ('health_content_manager')
) AS r(role)
CROSS JOIN (VALUES
  ('user:me_read'), ('user:me_patch'), ('user:sessions_read'), ('user:sessions_revoke')
) AS p(code)
ON CONFLICT (role, permission_code) WHERE deleted_at IS NULL DO NOTHING;

-- اپراتور پشتیبانی → کاربر عادی + مشاهده کاربران/لاگ
INSERT INTO role_permissions (role, permission_code)
SELECT 'support', code FROM (VALUES
  ('user:me_read'), ('user:me_patch'), ('user:sessions_read'), ('user:sessions_revoke'),
  ('admin:users_read'), ('admin:audit_read')
) AS p(code)
ON CONFLICT (role, permission_code) WHERE deleted_at IS NULL DO NOTHING;

-- مالی و اکانتنت → کاربر عادی + مشاهده کاربران/لاگ + 2FA (ادمین مالی)
INSERT INTO role_permissions (role, permission_code)
SELECT 'finance', code FROM (VALUES
  ('user:me_read'), ('user:me_patch'), ('user:sessions_read'), ('user:sessions_revoke'),
  ('admin:users_read'), ('admin:audit_read'), ('admin:2fa_verify')
) AS p(code)
ON CONFLICT (role, permission_code) WHERE deleted_at IS NULL DO NOTHING;

INSERT INTO role_permissions (role, permission_code)
SELECT 'accountant', code FROM (VALUES
  ('user:me_read'), ('user:me_patch'), ('user:sessions_read'), ('user:sessions_revoke'),
  ('admin:2fa_verify')
) AS p(code)
ON CONFLICT (role, permission_code) WHERE deleted_at IS NULL DO NOTHING;

-- ادمین/Super → همه مجوزها
INSERT INTO role_permissions (role, permission_code)
SELECT 'admin_super', code FROM permissions
ON CONFLICT (role, permission_code) WHERE deleted_at IS NULL DO NOTHING;

-- ---------- کاربر ادمین اولیه ----------
-- شماره از متغیر محیطی ADMIN_PHONE می‌آید (scripts/seed.js آن را به‌عنوان تنظیم
-- جلسه ست می‌کند). اگر ست نشده باشد، این بخش بی‌اثر است.
INSERT INTO users (phone, full_name, status)
SELECT p.admin_phone, 'مدیر سیستم', 'ACTIVE'
FROM (SELECT current_setting('ampet.admin_phone', true) AS admin_phone) p
WHERE p.admin_phone IS NOT NULL AND p.admin_phone <> ''
ON CONFLICT DO NOTHING;

INSERT INTO user_roles (user_id, role)
SELECT u.id, 'admin_super'
FROM users u
WHERE u.phone = nullif(current_setting('ampet.admin_phone', true), '')
ON CONFLICT (user_id, role) WHERE deleted_at IS NULL DO NOTHING;
