# apps/app — اپ Flutter (SP-00 اسکافولد + دیزاین‌سیستم)

> این پوشه فعلاً **اسکافولد دستی** است (توسط ابزار AI ساخته شده) چون Flutter SDK روی ماشین توسعه فعلی نصب نیست.
> با نصب Flutter، پوشه‌های پلتفرم (`android/`, `ios/`) با `flutter create .` تولید می‌شوند و کد `lib/` دست‌نخورده می‌ماند.

## گام‌های تکمیل (روی ماشین کارفرما)

```bash
cd apps/app
flutter create . --project-name ampet_app --platforms=android   # تولید android/ بدون تغییر lib/
flutter pub get
flutter analyze          # باید سبز باشد
flutter run              # صفحه گالری ۱۳ کامپوننت + RTL + فونت Vazirmatn
```

## محتوا

- `lib/design/tokens.dart` — توکن‌های قرارداد (رنگ/تایپوگرافی/فاصله/ابعاد لمسی) + `buildAmpetTheme()`
- `lib/design/components.dart` — **۱۳ کامپوننت استاندارد** (M-00.7)
- `lib/main.dart` — صفحه «گالری» برای بازبینی چشمی + RTL + سقف text-scale ۱۳۰٪

## معیار پذیرش M-00.7

- کنتراست متن ≥ ۴.۵:۱، ناحیه لمسی ≥ ۴۴dp، دکمه ۴۸dp
- `flutter analyze` سبز و گالری با `textScale=1.3` بدون بریدگی/همپوشانی