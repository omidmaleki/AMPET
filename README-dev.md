# راهنمای توسعه AMPET (README-dev.md)

> خروجی رسمی SP-00 — نحوه نصب، بالا آوردن، تست. جزئیات معماری در `Technical Architecture/Technical-Architecture.md` و نقشه در `ریزپروژه‌ها/README.md`.

## ۱. پیش‌نیازها (روی سیستم کارفرما)

| ابزار | نسخه | چک |
|-------|------|-----|
| Node.js | **20 LTS** (18/22 هم پذیرفته) | `node --version` |
| npm | 10+ | `npm --version` |
| Docker Desktop / Engine | Compose v2 | `docker compose version` |
| Git | 2.40+ | `git --version` |
| Flutter SDK | stable | `flutter doctor` |
| Android SDK + یک دستگاه اندروید | для تست اپ | `flutter devices` |

> **نکته توسعه روی این ماشین کنونی:** Git/Docker/Flutter هنوز نصب نشده‌اند؛ کد و تست‌های API (`npm test`) بدون آن‌ها اجرا می‌شود. گام‌های G/D/F تا نصب، در بخش «گام‌های نیازمند ابزار جانبی» بسته می‌مانند.

## ۲. نصب و بالا آوردن (حداقل مسیر)

```bash
# ۱) وابستگی‌ها
npm install

# ۲) زیرساخت (Postgres/Redis/MinIO)
cp .env.example .env          # ویندوز: copy .env.example .env
docker compose up -d
docker compose ps             # انتظار: هر سه healthy

# ۳) دیتابیس: ساخت دیتابیس + مهاجرت‌ها
npm run db:migrate            # up (جداول پایه Auth/User + pg_trgm)
npm run db:migrate:down       # تمرین rollback (ماده ۸.۵)

# ۴) اجرای API
npm run start:dev
# → http://localhost:3000/docs  (Swagger)
# → http://localhost:3000/api/v1/health
```

### بدون Docker (فعلاً روی این ماشین)
```bash
# Postgres/Redis در دسترس نیستند ← مهاجرت‌ها و تست‌های DB غیرفعال؛
# تست‌های قرارداد/envelope/nرخ‌گیر (in-memory) و Swagger همچنان سبزند.
npm run test -w @ampet/api
```

## ۳. دستورهای پرکاربرد

| فرمان | کار |
|-------|-----|
| `npm run lint` | ESLint + Prettier (api) |
| `npm test` | Jest — واحد/قرارداد (بدون نیاز DB برای اکثر تست‌ها) |
| `npm run test:e2e` | تست‌های e2e (نیازمند DATABASE_URL در CI) |
| `npm run docs:check` | تطبیق ۱۰۰٪ routeهای ثبت‌شده با OpenAPI `/docs` |
| `npm run db:migrate` / `db:migrate:down` | مهاجرت/برگشت (فایل‌های `apps/api/src/migrations/up|down`) |

## ۴. ساختار ریپو (SP-00 / M-00.1)

```
ampet/
  apps/
    api/          NestJS مونولیت ماژولار (auth, user, marketplace, payment, admin)
    app/          Flutter (Android first) — lib/design توکن‌ها
    web-admin/    Next.js — styles/tokens.css
  docs/           decision log, error-codes, backlog
  docker-compose.yml
  .github/workflows/ci.yml
  .env.example
```

## ۵. قراردادهای سراسری (که هیچ SPای از نو نمی‌نویسد)

- پاسخ موفق `{success:true, data, meta}` — میان‌افزار `X-Request-Id` (UUID)
- خطا `{success:false, error:{code, message, details[], request_id}}` — پیام فارسی
- نرخ‌گیر: عمومی ۶۰/دقیقه · پایه‌رداخت ۱۰/دقیقه · ادمین ۱۲۰/دقیقه · OTP ۳/۱۰دقیقه (429 + `Retry-After`)
- همه مسیرها زیر `api/v1`؛ Swagger در `/docs`
- soft-delete (`deleted_at`) + `created_at/updated_at` ISO + `audit_logs` فقط‌افزودنی (تریگر)
- پیامک mock: `logs/sms-mock.log` (همان امضای interface کاوه‌نگار)؛ درگاه mock با کلید `PAYMENT_GATEWAY`

## ۶. گام‌های نیازمند ابزار جانبی (روی ماشین کارفرما)

| گام | ابزار | دستور |
|-----|-------|-------|
| ریپو + اولین push | Git/GitHub | `git init && git add -A && git commit && git remote add origin <url> && git push -u origin main` |
| سرویس‌های پایه | Docker | `docker compose up -d` (بخش ۲) |
| اپ اندروید | Flutter | در `apps/app`: `flutter pub get && flutter run` |
| پنل وب | Node | در `apps/web-admin`: `npm install && npm run dev` |

## ۷. تحویل M0 (ماده ۳.۱)

- [ ] لینک ریپو روی GitHub کارفرما (دسترسی ادمین کارفرما — ماده ۶.۲)
- [ ] آدرس dev (`http://localhost:3000/docs` یا ساب‌دامنه تستی)
- [ ] این سند + `docs/backlog.md` + `docs/decisions.md`
- [ ] الحاقیه ماده ۲ (مونولیت ماژولار) امضا شده یا ماده ۲ اصلاح شده