# وضعیت پیاده‌سازی SP-01 (Auth) — گزارش صادقانه

> تاریخ: ۱۴۰۵/۰۷/۲۳ (۱۴ اکتبر ۲۰۲۶) | تهیه‌کننده: AI (OpenCode) | دامنه: `Main_Code/apps/api`
> این سند **مکملِ** `SP-00-SP-01-Acceptance-Report.md` است و وضعیت واقعی کد را (برخلاف ادعای اولیهٔ آن گزارش که فقط «اسکلت» بود) ثبت می‌کند.

## ۱. خلاصه اجرایی

پیش از این کار، تمام endpointهای SP-01 **placeholder** بودند (بدون لایه دیتابیس، بدون OTP واقعی، `RequirePermissionGuard` هاردکد `return true`).
اکنون مسیر «شماره موبایل → OTP → JWT/Refresh → پروفایل → نقش → نشست» **واقعی و ماشین‌تأییدشده** پیاده شده است.

- ✅ `build` سبز — `lint` سبز — **۳۴ تست پاس / ۳ skip** (تست‌های نیازمند DB).
- ⚠️ تست‌های یکپارچه روی Postgres هنوز اجرا نشده (Docker روی سیستم نصب نیست — مطابق تصمیم کاربر: «کد را بنویس، Docker بعداً»).

## ۲. وضعیت مایلاستون‌ها

| مایلاستون | وضعیت | جزئیات |
|-----------|-------|--------|
| **M-01.1** گسترش اسکیما | ✅ کامل | `002-user-auth.sql` (۳ جدول جدید + ALTER `users`/`sessions`) + `down/002-user-auth.sql` + `seed/002-seed-sp01.sql` (۸ مجوز + ماتریس نقش‌ها + ادمین اولیه از `ADMIN_PHONE`). باگ تکرار ایندکس `ix_sessions_user_revoked` (تعریف‌شده در 001) رفع شد. |
| **M-01.2** OTP request/verify | ✅ کامل | کد ۵ رقمی `randomInt` + هش HMAC-SHA256 (`OTP_HASH_PEPPER`)؛ سقف ۳/۱۰دقیقه روی **شماره و IP**؛ انقضا ۱۲۰ ثانیه؛ قفل ۱۵دقیقه پس از ۳ تلاش + `Retry-After: 900`؛ `SMS-OTP`/`SMS-OTP-RESEND`/`SMS-REGISTER`؛ `403 ACCOUNT_BLOCKED` بدون ذکر دلیل. |
| **M-01.3** JWT/Refresh/نشست | ✅ کامل | Access ۱۵دقیقه (ادمین ۱۰)؛ refresh ۳۰روزهٔ چرخشی با `jti` و هش sha256 در `sessions.refresh_hash`؛ استفادهٔ مجدد → ابطال همهٔ نشست‌ها + `auth.refresh_reuse`؛ `/auth/refresh`، `/auth/logout`، `GET /me/sessions`، revoke/revoke-all؛ تشخیص دستگاه جدید + `SMS-NEW-DEVICE`. |
| **M-01.4** پروفایل/RBAC/2FA | 🟡 عمدتاً کامل | `GET /me`, `PATCH /me` (نام الزامی + `TERMS_NOT_ACCEPTED`)؛ `RequirePermissionGuard` **واقعی** (بر پایهٔ `permissions`/`role_permissions`) + ثبت تلاش ممنوع در `audit_logs`؛ `PATCH /admin/users/{id}/role` با `before/after` + ابطال نشست‌ها؛ 2FA اسکلت (`POST /admin/auth/2fa/verify`, `2FA_REQUIRED`). **باقی‌مانده:** فیلد `referral_code` در `/me` (جدول referrals → SP-13). |
| **M-01.5** حذف حساب ۱۴ روزه | ⬜ انجام‌نشده | `POST /me/delete-request`, `/cancel`, registry ۹ مانع، کرون ۰۳:۰۰، ناشناس‌سازی + هش شماره، ثبت‌نام مجدد پس از ۳۰ روز. |
| **M-01.6** صفحات Flutter + تحویل | ⬜ انجام‌نشده | ۴+ صفحه اپ، RTL/ارقام فارسی، `flutter test`، صورت‌جلسه M1. |

## ۳. فایل‌های افزوده/تغییر‌یافته (این اینکرمنت)

**جدید — لایه دیتابیس:** `src/database/{database.module,database.service,database.constants}.ts`
**جدید — Auth:** `src/modules/auth/` (auth.{controller,service,module,types,roles}.ts • otp.service.ts • otp.util.ts • session.service.ts • token.service.ts • jwt-auth.guard.ts • current-user.decorator.ts • request-context.ts • dto/auth.dto.ts • repositories/{user,otp,session,audit}.repository.ts)
**جدید — عمومی:** `src/common/persian.ts`
**بازنویسی:** `src/modules/user/session.controller.ts`، `src/modules/admin/admin.controller.ts`، `src/modules/{user,admin}/*.module.ts`، `src/common/guards/require-permission.guard.ts`
**مهاجرت/seed:** `src/migrations/up/002-user-auth.sql` (اصلاح)، `src/migrations/down/002-user-auth.sql`، `src/migrations/seed/002-seed-sp01.sql`، `scripts/seed.js`
**تست‌ها:** `test/unit/otp.service.spec.ts` (۹ تست)، `test/unit/token.service.spec.ts` (۶ تست)، اصلاح `test/docs.swagger.spec.ts` (مسیرهای پارامتری)، `test/migrations.spec.ts` (شمارش ۸)
**متن‌ها:** فیلتر خطا حالا هدر `Retry-After` را از `details.retry_after_seconds` ست می‌کند؛ گارد نرخ برای سطل OTP پیام دقیق سند را می‌دهد.

## ۴. تصمیم‌های ثبت‌شده
`docs/decisions.md` → D-043 (هش OTP)، D-044 (قفل ۱۵دقیقه)، D-045 (refresh چرخشی/استفادهٔ مجدد)، D-046 (2FA ادمین)، D-047 (لایهٔ `pg.Pool` بدون ORM).

## ۵. نحوهٔ اجرا (وقتی Docker/Postgres آماده شد)

```bash
cd Main_Code
cp .env.example .env            # سپس ADMIN_PHONE و سکرت‌ها را ست کنید
docker compose up -d postgres redis minio
npm run db:migrate -w @ampet/api
npm run db:seed -w @ampet/api
npm test -w @ampet/api          # تست‌های DB خودکار فعال می‌شوند
```

## ۶. کار باقی‌مانده (ترتیب پیشنهادی)
1. **تست‌های یکپارچهٔ DB** با نام‌های دقیق DoD (`otp_*`, `session_*`, `rbac_*`, `deletion_*`) — روی دیتابیس تازه، skip بدون `DATABASE_URL`.
2. **M-01.5** حذف حساب ۱۴ روزه (registry موانع + کرون).
3. **M-01.6** صفحات Flutter + صورت‌جلسه M1.
4. `referral_code` در `/me` پس از SP-13.
