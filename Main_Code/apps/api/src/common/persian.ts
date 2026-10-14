/** ابزار ارقام فارسی (SP-01 M-01.6 — «ارقام فارسی» در UI Copy). */
const PERSIAN_DIGITS = ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹'];

/** تبدیل ارقام لاتین یک رشته به ارقام فارسی. */
export function toPersianDigits(value: string | number): string {
  return String(value).replace(/\d/g, (d) => PERSIAN_DIGITS[Number(d)]);
}
