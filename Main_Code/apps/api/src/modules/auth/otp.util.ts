import { createHmac, randomInt, timingSafeEqual } from 'crypto';

/**
 * ابزارهای OTP (SP-01 / M-01.2):
 * - کد ۵ رقمی با `randomInt` رمزنگاری‌امن (بدون Math.random)
 * - ذخیره فقط **هش HMAC-SHA256** با pepper محیطی (بدون متن کد در DB)
 * - مقایسه timing-safe
 */

/** تولید کد ۵ رقمی «۰۱۲۳۴» شکل (leading zero حفظ می‌شود). */
export function generateOtpCode(): string {
  return String(randomInt(0, 100_000)).padStart(5, '0');
}

/** pepper از محیط؛ در dev پیش‌فرض امن نیست ولی یکسان است. */
export function otpPepper(): string {
  return process.env.OTP_HASH_PEPPER ?? 'ampet_dev_otp_pepper_change_me';
}

/** هش یک‌طرفه کد بر پایه (phone, code, pepper). */
export function hashOtp(phone: string, code: string, pepper = otpPepper()): string {
  return createHmac('sha256', pepper).update(`${phone}:${code}`).digest('hex');
}

/** مقایسهٔ timing-safe هش. */
export function verifyOtpHash(phone: string, code: string, hash: string): boolean {
  const candidate = hashOtp(phone, code);
  const a = Buffer.from(candidate);
  const b = Buffer.from(hash);
  if (a.length !== b.length) return false;
  return timingSafeEqual(a, b);
}
