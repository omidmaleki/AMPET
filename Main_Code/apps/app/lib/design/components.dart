// AMPET — ۱۳ کامپوننت استاندارد دیزاین‌سیستم (SP-00 / M-00.7)
// همه با توکن‌های tokens.dart ساخته شده‌اند. Gallery در lib/main.dart نمایش می‌دهد.
import 'dart:async';
import 'package:flutter/material.dart';
import 'tokens.dart';

// ۱) Button
class AmpetButton extends StatelessWidget {
  const AmpetButton({
    super.key,
    required this.label,
    this.onPressed,
    this.variant = AmpetButtonVariant.primary,
    this.loading = false,
    this.icon,
  });

  final String label;
  final VoidCallback? onPressed;
  final AmpetButtonVariant variant;
  final bool loading;
  final IconData? icon;

  @override
  Widget build(BuildContext context) {
    final bg = switch (variant) {
      AmpetButtonVariant.primary => AmpetColors.primary,
      AmpetButtonVariant.accent => AmpetColors.accent,
      AmpetButtonVariant.ghost => Colors.transparent,
    };
    final fg = variant == AmpetButtonVariant.ghost ? AmpetColors.primary : Colors.white;
    return SizedBox(
      height: AmpetSizes.buttonHeight,
      width: double.infinity,
      child: ElevatedButton.icon(
        onPressed: loading ? null : onPressed,
        style: ElevatedButton.styleFrom(
          backgroundColor: bg,
          foregroundColor: fg,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(AmpetRadius.md),
          ),
        ),
        icon: loading
            ? const SizedBox(
                width: 18,
                height: 18,
                child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
              )
            : (icon != null ? Icon(icon) : const SizedBox.shrink()),
        label: Text(label),
      ),
    );
  }
}

enum AmpetButtonVariant { primary, accent, ghost }

// ۲) Input
class AmpetInput extends StatelessWidget {
  const AmpetInput({
    super.key,
    required this.label,
    this.hint,
    this.errorText,
    this.controller,
    this.keyboardType,
  });

  final String label;
  final String? hint;
  final String? errorText;
  final TextEditingController? controller;
  final TextInputType? keyboardType;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: const TextStyle(fontWeight: AmpetTypography.medium)),
        const SizedBox(height: AmpetSpacing.xs),
        TextField(
          controller: controller,
          keyboardType: keyboardType,
          textDirection: TextDirection.rtl,
          decoration: InputDecoration(
            hintText: hint,
            errorText: errorText,
            contentPadding: const EdgeInsets.symmetric(horizontal: AmpetSpacing.md),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(AmpetRadius.md),
            ),
          ),
        ),
      ],
    );
  }
}

// ۳) Chip
class AmpetChip extends StatelessWidget {
  const AmpetChip({super.key, required this.label, this.selected = false, this.onTap});
  final String label;
  final bool selected;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(
          horizontal: AmpetSpacing.md,
          vertical: AmpetSpacing.sm,
        ),
        decoration: BoxDecoration(
          color: selected ? AmpetColors.primary.withValues(alpha: 0.1) : AmpetColors.card,
          border: Border.all(color: selected ? AmpetColors.primary : AmpetColors.border),
          borderRadius: BorderRadius.circular(AmpetRadius.pill),
        ),
        child: Text(
          label,
          style: TextStyle(
            color: selected ? AmpetColors.primary : AmpetColors.textSecondary,
          ),
        ),
      ),
    );
  }
}

// ۴) Card
class AmpetCard extends StatelessWidget {
  const AmpetCard({super.key, required this.child, this.padding});
  final Widget child;
  final EdgeInsetsGeometry? padding;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: padding ?? const EdgeInsets.all(AmpetSpacing.md),
      decoration: BoxDecoration(
        color: AmpetColors.card,
        border: Border.all(color: AmpetColors.border),
        borderRadius: BorderRadius.circular(AmpetRadius.lg),
      ),
      child: child,
    );
  }
}

// ۵) Badge
class AmpetBadge extends StatelessWidget {
  const AmpetBadge({super.key, required this.label, this.color});
  final String label;
  final Color? color;

  @override
  Widget build(BuildContext context) {
    final c = color ?? AmpetColors.accent;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: AmpetSpacing.sm, vertical: 2),
      decoration: BoxDecoration(
        color: c.withValues(alpha: 0.12),
        borderRadius: BorderRadius.circular(AmpetRadius.sm),
      ),
      child: Text(label, style: TextStyle(color: c, fontSize: AmpetTypography.caption)),
    );
  }
}

// ۶) Bottom Sheet
Future<void> showAmpetBottomSheet(BuildContext context, Widget child) {
  return showModalBottomSheet<void>(
    context: context,
    backgroundColor: AmpetColors.card,
    shape: const RoundedRectangleBorder(
      borderRadius: BorderRadius.vertical(top: Radius.circular(AmpetRadius.lg)),
    ),
    builder: (_) => Padding(
      padding: const EdgeInsets.all(AmpetSpacing.lg),
      child: child,
    ),
  );
}

// ۷) Modal
Future<void> showAmpetModal(BuildContext context, Widget child) {
  return showDialog<void>(
    context: context,
    builder: (_) => AlertDialog(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(AmpetRadius.lg)),
      content: child,
    ),
  );
}

// ۸) Toast (۳ ثانیه)
void showAmpetToast(BuildContext context, String message, {bool error = false}) {
  ScaffoldMessenger.of(context).showSnackBar(
    SnackBar(
      content: Text(message),
      backgroundColor: error ? AmpetColors.danger : AmpetColors.primary,
      duration: const Duration(seconds: 3),
    ),
  );
}

// ۹) Skeleton
class AmpetSkeleton extends StatelessWidget {
  const AmpetSkeleton({super.key, this.height = 16, this.width = double.infinity});
  final double height;
  final double width;

  @override
  Widget build(BuildContext context) {
    return Container(
      height: height,
      width: width,
      decoration: BoxDecoration(
        color: AmpetColors.border,
        borderRadius: BorderRadius.circular(AmpetRadius.sm),
      ),
    );
  }
}

// ۱۰) Empty
class AmpetEmpty extends StatelessWidget {
  const AmpetEmpty({super.key, required this.message, this.icon = Icons.inbox_outlined});
  final String message;
  final IconData icon;

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Icon(icon, size: 48, color: AmpetColors.textSecondary),
        const SizedBox(height: AmpetSpacing.sm),
        Text(message, style: const TextStyle(color: AmpetColors.textSecondary)),
      ],
    );
  }
}

// ۱۱) TabBar
class AmpetTabBar extends StatelessWidget {
  const AmpetTabBar({super.key, required this.tabs, this.controller});
  final List<String> tabs;
  final TabController? controller;

  @override
  Widget build(BuildContext context) {
    return TabBar(
      controller: controller,
      labelColor: AmpetColors.primary,
      unselectedLabelColor: AmpetColors.textSecondary,
      indicatorColor: AmpetColors.primary,
      tabs: tabs.map((t) => Tab(text: t)).toList(),
    );
  }
}

// ۱۲) Pull-to-Refresh
class AmpetPullToRefresh extends StatelessWidget {
  const AmpetPullToRefresh({super.key, required this.onRefresh, required this.child});
  final Future<void> Function() onRefresh;
  final Widget child;

  @override
  Widget build(BuildContext context) {
    return RefreshIndicator(
      color: AmpetColors.primary,
      onRefresh: onRefresh,
      child: child,
    );
  }
}

// ۱۳) Pagination
class AmpetPagination extends StatelessWidget {
  const AmpetPagination({
    super.key,
    required this.page,
    required this.totalPages,
    required this.onPageChanged,
  });
  final int page;
  final int totalPages;
  final ValueChanged<int> onPageChanged;

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        IconButton(
          onPressed: page > 1 ? () => onPageChanged(page - 1) : null,
          icon: const Icon(Icons.chevron_right),
        ),
        Text('صفحه $page از $totalPages'),
        IconButton(
          onPressed: page < totalPages ? () => onPageChanged(page + 1) : null,
          icon: const Icon(Icons.chevron_left),
        ),
      ],
    );
  }
}