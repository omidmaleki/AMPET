// AMPET Design Tokens — SP-00 / M-00.7
// منبع: project-document.md ۱۱۳۳-۱۲۶۲ (دیزاین‌سیستم، فریز ۱۴۰۵/۰۷/۱۴)
// قاعده: تغییر هر مقدار = مغایرت با قرارداد (فقط با الحاقیه). تست: test/unit/design-tokens.spec.ts
import 'package:flutter/material.dart';

class AmpetColors {
  /// رنگ اصلی برند
  static const Color primary = Color(0xFF0F5D4A); // #0F5D4A
  static const Color primaryDark = Color(0xFF0B4537);
  static const Color primaryLight = Color(0xFF1B7A63);

  /// رنگ تأکیدی (طلایی)
  static const Color accent = Color(0xFFD4AF37); // #D4AF37
  static const Color accentDark = Color(0xFFB8942A);

  /// متن و سطح
  static const Color textPrimary = Color(0xFF111827); // #111827
  static const Color textSecondary = Color(0xFF6B7280);
  static const Color surface = Color(0xFFF9FAFB); // #F9FAFB
  static const Color card = Color(0xFFFFFFFF);
  static const Color border = Color(0xFFE5E7EB);

  /// وضعیت‌ها
  static const Color success = Color(0xFF15803D);
  static const Color warning = Color(0xFFB45309);
  static const Color danger = Color(0xFFB91C1C);
  static const Color info = Color(0xFF1D4ED8);

  /// نگاشت قراردادی رنگ‌ها (snapshot — نباید تغییر کند)
  static const Map<String, String> contractHex = {
    'primary': '#0F5D4A',
    'accent': '#D4AF37',
    'text': '#111827',
    'surface': '#F9FAFB',
  };
}

class AmpetTypography {
  static const String fontFamily = 'Vazirmatn';
  static const double h1 = 24;
  static const double h2 = 20;
  static const double h3 = 18;
  static const double body = 14;
  static const double caption = 12;
  static const FontWeight regular = FontWeight.w400;
  static const FontWeight medium = FontWeight.w500;
  static const FontWeight bold = FontWeight.w700;
}

class AmpetSpacing {
  static const double xs = 4;
  static const double sm = 8;
  static const double md = 16;
  static const double lg = 24;
  static const double xl = 32;
}

class AmpetRadius {
  static const double sm = 8;
  static const double md = 12;
  static const double lg = 16;
  static const double pill = 999;
}

class AmpetSizes {
  /// حداقل ناحیه لمسی (دسترس‌پذیری) و ارتفاع دکمه اصلی
  static const double minTouch = 44;
  static const double buttonHeight = 48;
  static const double inputHeight = 48;
  static const double icon = 24;
  static const double maxTextScale = 1.3; // تحمل ۱۳۰٪
}

/// تم سراسری اپ — RTL + فونت Vazirmatn + رنگ قرارداد
ThemeData buildAmpetTheme() {
  final base = ThemeData.light(useMaterial3: true);
  return base.copyWith(
    colorScheme: base.colorScheme.copyWith(
      primary: AmpetColors.primary,
      secondary: AmpetColors.accent,
      surface: AmpetColors.surface,
      error: AmpetColors.danger,
    ),
    fontFamily: AmpetTypography.fontFamily,
    scaffoldBackgroundColor: AmpetColors.surface,
  );
}