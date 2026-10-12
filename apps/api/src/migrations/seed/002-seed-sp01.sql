-- SP-01 M-01.1 — seed نقش‌ها + مجوزها + ادمین اولیه (از .env)
-- فقط در staging/dev. در prod از اسکریپت جدا اجرا می‌شود.

INSERT INTO permissions (code, name, description) VALUES
('user:me_read', 'پروفایل', 'مشاهده پروفایل خود'),
('user:me_patch', 'ویرایش پروفایل', 'ویرایش نام/نقش'),
('user:sessions_read', 'نشست‌ها', 'لیست نشست‌ها'),
('user:sessions_revoke', 'ابطال نشست', 'باطل کردن یک نشست'),
('admin:users_read', 'لیست کاربران', 'مشاهده کاربران'),
('admin:users_role_patch', 'تغییر نقش', 'تغییر نقش کاربر'),
('admin:audit_read', 'لاگ', 'مشاهده audit_logs'),
('admin:2fa_verify', 'تأیید 2FA', 'تأیید کد ادمین مالی/Super')
ON CONFLICT (code) DO NOTHING;

-- ۸ نقش + ماتریس (خلاصه؛ کامل در SP-01 مرحله ۴)
-- customer, seller, provider, admin_super, support, accountant, content_manager
-- (برای سادگی در این seed فقط نام نقش مقداردهی می‌شود؛ matrix در کد تأیید می‌شود)
