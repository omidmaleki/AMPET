import { SetMetadata } from '@nestjs/common';

export interface RateLimitOptions {
  /** تعداد مجاز در پنجره */
  limit: number;
  /** طول پنجره بر حسب میلی‌ثانیه */
  windowMs: number;
  /** scope کلید: 'ip' | 'user' | 'ip+user' (پیش‌فرض ip) */
  scope?: 'ip' | 'user' | 'ip+user';
  /** نام سطل (برای پیام دقیق؛ مثلاً 'otp' ⇒ پیام اختصاصی OTP) */
  name?: string;
}

export const RATE_LIMIT_METADATA = 'rate_limit';

/**
 * تعیین سقف نرخ برای یک route — اگر نباشد، از `resolveBucketByPath`
 * سقف پیش‌فرض مسیر (۶۰/۱۲۰/۱۰ و OTP ۳/۱۰دقیقه) اعمال می‌شود.
 */
export const RateLimit = (options: RateLimitOptions) => SetMetadata(RATE_LIMIT_METADATA, options);
