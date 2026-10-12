import { Module } from '@nestjs/common';

/**
 * ماژول Auth — **بدون کد فیچر در SP-00** (فقط مرز ماژول).
 * پیاده‌سازی OTP/JWT/Refresh/RBAC → SP-01.
 * مرز سخت: این ماژول جدول‌های خودش را از schema جدا می‌خواند و بدون join بین‌ماژولی است.
 */
@Module({})
export class AuthModule {}
