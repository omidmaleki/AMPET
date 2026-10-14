# فهرست کدهای خطا (Error Code Catalog) — AMPET

> منبع پایه: `project-document.md:4651-4680` (بخش «کدهای HTTP و کدهای منطقی»).
> قاعده (README قاعده ۵ + SP-12/13/14): همه پاسخ‌های خطا `{success:false, error:{code, message, details[], request_id}}` با `message` فارسی دقیق از UI Copy.
> فایل اجرایی هم‌ارز: `Main_Code/apps/api/src/common/error-codes.ts` — این سند باید با آن در sync بماند (تست contract چک می‌کند).

## ۱. کدهای HTTP عمومی

| HTTP | معنی | کد منطقی نمونه |
|------|------|----------------|
| 200 | موفق | — |
| 201 | ایجاد شد | `CREATED` |
| 400 | بدنه نامعتبر | `VALIDATION_ERROR` |
| 401 | بدون توکن / منقضی | `TOKEN_EXPIRED` |
| 403 | مجوز ندارد | `FORBIDDEN_ROLE` |
| 404 | پیدا نشد | `NOT_FOUND` |
| 409 | تداخل | `HOLD_EXPIRED`, `ORDER_STATE_CONFLICT` |
| 422 | منطقی/پیش‌شرط | `STOCK_UNAVAILABLE`, `CANCEL_NOT_ALLOWED`, `RETURN_WINDOW_CLOSED` |
| 429 | محدودیت نرخ | `RATE_LIMIT_EXCEEDED` (+ هدر `Retry-After`) |
| 500 | خطای داخلی | `INTERNAL_ERROR` |
| 502/503 | خطای درگاه/سرویس خارجی | `PAYMENT_GATEWAY_FAILED` |

## ۲. کدهای منطقی پرتکرار (سند پایه)

`OTP_INVALID` / `OTP_EXPIRED` / `OTP_TRIES_EXCEEDED` · `STOCK_UNAVAILABLE` / `HOLD_EXPIRED` · `PAYMENT_GATEWAY_FAILED` / `REFUND_PENDING` · `WALLET_INSUFFICIENT` · `CANCEL_NOT_ALLOWED` · `RETURN_WINDOW_CLOSED` · `DISCOUNT_MIN_NOT_MET` / `DISCOUNT_EXPIRED` · `REFERRAL_SELF_INVITE` / `REFERRAL_LIMIT` · `TERMS_NOT_ACCEPTED` · `FORCE_UPDATE_REQUIRED`

## ۳. کدهای «تصمیم» — افزوده‌شده در SPها (ثبت در Swagger الزامی)

| کد | HTTP | معنی | مبدأ |
|----|------|------|------|
| `PRICE_OUT_OF_BAND` | 422 | خارج از بازه بازار (میانه ±۴۰٪) | SP-03 (D-005) |
| `ADDRESS_IN_USE` | 409 | آدرس متصل به سفارش در جریان | SP-02 |
| `ADDRESS_DEFAULT_REQUIRED` | 422 | حداقل یک آدرس باید پیش‌فرض باشد | SP-02 |
| `PET_LIMIT_REACHED` | 422 | سقف ۲۰ حیوان | SP-02 |
| `PET_HAS_ACTIVE_BOOKING` | 422 | حیوان نوبت آینده دارد | SP-02 |
| `SHARE_LINK_EXPIRED` | 422 | لینک اشتراک منقضی | SP-02 |
| `RECORD_EDIT_WINDOW_CLOSED` | 409 | قفل ۲۴ ساعته سوابق | SP-02 |
| `DELIVERY_CODE_INVALID` | 422 | کد تحویل اشتباه | SP-08 |
| `EARLY_WITHDRAWAL_NOT_ALLOWED` | 422 | برداشت زودهنگام در چرخه ۱ | SP-09 |
| `WALLET_DEBT_PENDING` | 422 | کیف پول منفی | SP-09 |
| `RETURN_NOT_ELIGIBLE` | 422 | استثناهای مرجوعی (دارو/غذای باز...) | SP-10 |
| `RETURN_APPEAL_WINDOW_CLOSED` | 422 | مهلت ۷ روز اعتراض | SP-10 |
| `TEMPLATE_NOT_FOUND` | 422 | کد قالب خارج از ۷۸ قالب | SP-11 |
| `NOTIFICATION_SETTINGS_CONFLICT` | 422 | لغو یادآوری مالی/عملیاتی | SP-11 |
| `NOTIFICATION_CHANNEL_FAILED` | 503 | شکست کانال خارجی (۲ تلاش) | SP-11 |
| `REVIEW_DUPLICATE` | 409 | نظر تکراری | SP-12 |
| `REVIEW_NOT_ELIGIBLE` | 422 | فقط برای سفارش تحویل‌شده | SP-12 |
| `REVIEW_WINDOW_CLOSED` | 422 | مهلت ۳۰ روز نظر | SP-12 |
| `FAVORITE_LIMIT_REACHED` | 422 | سقف ۵۰۰ علاقه‌مندی | SP-12 |
| `DISCOUNT_EXHAUSTED` | 422 | سقف مصرف کد | SP-13 |
| `DISCOUNT_ALREADY_APPLIED` | 422 | فقط ۱ کد | SP-13 |
| `DISCOUNT_SCOPE_MISMATCH` | 422 | کد فقط برای فروشگاه X | SP-13 |
| `LOYALTY_CAP_EXCEEDED` | 422 | حداکثر ۲۰٪ با امتیاز | SP-13 |
| `TICKET_LIMIT_REACHED` | 409 | حداکثر ۱۰ تیکت باز | SP-14 |
| `CHAT_THREAD_CLOSED` | 409 | گفتگو بسته/فقط خواندنی | SP-14 |
| `REOPEN_WINDOW_CLOSED` | 422 | مهلت بازگشایی گذشته | SP-14 |

## ۴. انطباق با اجرا

- [ ] همه کدهای بالا در `Main_Code/apps/api/src/common/error-codes.ts` موجودند.
- [ ] همه مسیرهای ثبت‌شده در `/docs` (OpenAPI) کدهای خطای خود را اعلام می‌کنند (docs:check).
- [ ] هیچ کد پرتکراری بین فهرست بالا و سند پایه مغایر نیست.