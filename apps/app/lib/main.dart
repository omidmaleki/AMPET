// AMPET App entrypoint — SP-00 / M-00.7
// RTL کامل + فونت Vazirmatn + Gallery ۱۳ کامپوننت (برای بازبینی بصری کارفرما).
import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'design/components.dart';
import 'design/tokens.dart';

void main() => runApp(const AmpetApp());

class AmpetApp extends StatelessWidget {
  const AmpetApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'AMPET',
      debugShowCheckedModeBanner: false,
      theme: buildAmpetTheme(),
      locale: const Locale('fa', 'IR'),
      supportedLocales: const [Locale('fa', 'IR')],
      localizationsDelegates: const [
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      builder: (context, child) => Directionality(
        textDirection: TextDirection.rtl,
        child: MediaQuery(
          // سقف بزرگ‌نمایی ۱۳۰٪ (متن نباید ببرد)
          data: MediaQuery.of(context).copyWith(
            textScaler: MediaQuery.of(context).textScaler.clamp(
              minScaleFactor: 1.0,
              maxScaleFactor: AmpetSizes.maxTextScale,
            ),
          ),
          child: child!,
        ),
      ),
      home: const GalleryPage(),
    );
  }
}

/// صفحه گالری ۱۳ کامپوننت — پذیرش چشمی M-00.7
class GalleryPage extends StatefulWidget {
  const GalleryPage({super.key});

  @override
  State<GalleryPage> createState() => _GalleryPageState();
}

class _GalleryPageState extends State<GalleryPage> {
  int _page = 2;
  int _selectedTab = 0;
  final _nameController = TextEditingController();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: AmpetColors.primary,
        foregroundColor: Colors.white,
        title: const Text('گالری دیزاین‌سیستم AMPET'),
      ),
      body: AmpetPullToRefresh(
        onRefresh: () async => Future<void>.delayed(const Duration(milliseconds: 400)),
        child: ListView(
          padding: const EdgeInsets.all(AmpetSpacing.md),
          children: [
            const _Section('۱. Button'),
            AmpetButton(label: 'دکمه اصلی', onPressed: () {}),
            const SizedBox(height: AmpetSpacing.sm),
            AmpetButton(label: 'دکمه ثانویه', variant: AmpetButtonVariant.accent, onPressed: () {}),
            const _Section('۲. Input'),
            AmpetInput(label: 'نام', hint: 'مثلاً آمپت', controller: _nameController),
            const _Section('۳. Chip'),
            Wrap(spacing: AmpetSpacing.sm, children: const [
              AmpetChip(label: 'سگ', selected: true),
              AmpetChip(label: 'گربه'),
              AmpetChip(label: 'پرنده'),
            ]),
            const _Section('۴. Card'),
            const AmpetCard(child: Text('محتوای نمونه کارت')),
            const _Section('۵. Badge'),
            const Wrap(spacing: 8, children: [
              AmpetBadge(label: 'جدید'),
              AmpetBadge(label: 'در انتظار', color: AmpetColors.warning),
            ]),
            const _Section('۶/۷. Bottom Sheet & Modal'),
            Row(children: [
              Expanded(
                child: AmpetButton(
                  label: 'BottomSheet',
                  variant: AmpetButtonVariant.ghost,
                  onPressed: () => showAmpetBottomSheet(context, const Text('نمونه شیت')),
                ),
              ),
              Expanded(
                child: AmpetButton(
                  label: 'Modal',
                  variant: AmpetButtonVariant.ghost,
                  onPressed: () => showAmpetModal(context, const Text('نمونه مودال')),
                ),
              ),
            ]),
            const _Section('۸. Toast'),
            AmpetButton(
              label: 'نمایش Toast',
              variant: AmpetButtonVariant.ghost,
              onPressed: () => showAmpetToast(context, 'ذخیره شد'),
            ),
            const _Section('۹. Skeleton'),
            const AmpetSkeleton(height: 20),
            const SizedBox(height: 8),
            const AmpetSkeleton(height: 20, width: 160),
            const _Section('۱۰. Empty'),
            const SizedBox(height: 120, child: AmpetEmpty(message: 'این دسته فعلاً خالی است')),
            const _Section('۱۱. TabBar'),
            AmpetTabBar(tabs: const ['همه', 'سگ', 'گربه'], controller: TabController(length: 3, vsync: _NoopVsync())),
            const _Section('۱۲. Pull-to-Refresh'),
            const Text('کل لیست را بکشید تا رفرش شود'),
            const _Section('۱۳. Pagination'),
            AmpetPagination(
              page: _page,
              totalPages: 5,
              onPageChanged: (p) => setState(() => _page = p),
            ),
            Text('تب فعال: $_selectedTab', style: const TextStyle(color: AmpetColors.textSecondary)),
          ],
        ),
      ),
    );
  }
}

class _Section extends StatelessWidget {
  const _Section(this.title);
  final String title;

  @override
  Widget build(BuildContext context) => Padding(
        padding: const EdgeInsets.only(top: AmpetSpacing.lg, bottom: AmpetSpacing.sm),
        child: Text(title, style: const TextStyle(fontSize: AmpetTypography.h3, fontWeight: AmpetTypography.bold)),
      );
}

class _NoopVsync implements TickerProvider {
  @override
  Ticker createTicker(TickerCallback onTick) => Ticker(onTick);
}