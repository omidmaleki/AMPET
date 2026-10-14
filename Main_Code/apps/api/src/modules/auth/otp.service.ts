import { HttpStatus, Inject, Injectable } from '@nestjs/common';
import { ErrorCode } from '../../common/error-codes';
import { ApiException } from '../../common/exceptions/api.exception';
import { toPersianDigits } from '../../common/persian';
import { RATE_LIMITER } from '../../common/rate-limit/rate-limit.module';
import { RateLimiter } from '../../common/rate-limit/rate-limiter.service';
import { SMS_PROVIDER } from '../../providers/sms/sms-provider';
import type { SmsProvider } from '../../providers/sms/sms-provider';
import { generateOtpCode, hashOtp, verifyOtpHash } from './otp.util';
import { OtpRepository } from './repositories/otp.repository';
import { UserRow, UserRepository } from './repositories/user.repository';

/** ثابت‌های OTP (SP-01 M-01.2 — قرارداد ماده ۳.۲ + project-document.md:1284). */
export const OTP_TTL_SECONDS = 120;
export const OTP_MAX_ATTEMPTS = 3;
export const OTP_LOCK_SECONDS = 900; // قفل ۱۵ دقیقه (مغایرت ۶۰ثانیه TA §۷.۱ در ریسک SP-01 ثبت شد)
export const OTP_REQUEST_LIMIT = 3;
export const OTP_REQUEST_WINDOW_MS = 10 * 60 * 1000;

export interface OtpVerifyResult {
  userId: string;
  isNewUser: boolean;
  user: UserRow;
}

/**
 * سرویس OTP (SP-01 M-01.2):
 * - درخواست: اعتبار شماره → سقف ۳/۱۰دقیقه روی **شماره و IP** → کد ۵ رقمی (فقط هش) → پیامک mock
 * - تأیید: انقضا (`OTP_EXPIRED`)، شمارش تلاش، قفل ۱۵ دقیقه (`OTP_TRIES_EXCEEDED` + Retry-After)
 */
@Injectable()
export class OtpService {
  constructor(
    private readonly otpRepo: OtpRepository,
    private readonly userRepo: UserRepository,
    @Inject(SMS_PROVIDER) private readonly sms: SmsProvider,
    @Inject(RATE_LIMITER) private readonly limiter: RateLimiter,
  ) {}

  /** اعتبار قالب شماره ایران؛ پیام دقیق UI Copy. */
  assertPhone(phone: string): void {
    if (!/^09\d{9}$/.test(phone)) {
      throw ApiException.validation('شماره موبایل معتبر نیست. ۱۱ رقم وارد کنید', [
        { field: 'phone', reason: 'invalid_format' },
      ]);
    }
  }

  private assertCode(code: string): void {
    if (!/^\d{5}$/.test(code)) {
      throw ApiException.validation('کد تأیید ۵ رقمی الزامی است', [{ field: 'code' }]);
    }
  }

  async request(
    phone: string,
    purpose: string,
    ip: string | null,
  ): Promise<{ message: string; expires_in: number; is_resend: boolean }> {
    this.assertPhone(phone);

    const phoneHit = await this.limiter.increment(
      `otp:req:phone:${phone}`,
      OTP_REQUEST_LIMIT,
      OTP_REQUEST_WINDOW_MS,
    );
    const ipHit = ip
      ? await this.limiter.increment(`otp:req:ip:${ip}`, OTP_REQUEST_LIMIT, OTP_REQUEST_WINDOW_MS)
      : { ok: true, count: 0, retryAfterMs: 0 };

    const blocked = !phoneHit.ok ? phoneHit : !ipHit.ok ? ipHit : null;
    if (blocked) {
      const retryAfterSeconds = Math.max(1, Math.ceil(blocked.retryAfterMs / 1000));
      const minutes = Math.max(1, Math.ceil(blocked.retryAfterMs / 60_000));
      throw new ApiException(
        ErrorCode.RATE_LIMIT_EXCEEDED,
        HttpStatus.TOO_MANY_REQUESTS,
        `تعداد درخواست‌های شما زیاد است. ${toPersianDigits(minutes)} دقیقه دیگر دوباره تلاش کنید`,
        [{ retry_after_seconds: retryAfterSeconds }],
      );
    }

    const isResend = (await this.otpRepo.latestActive(phone, purpose)) !== null;
    await this.otpRepo.invalidateActive(phone, purpose);

    const code = generateOtpCode();
    const expiresAt = new Date(Date.now() + OTP_TTL_SECONDS * 1000);
    await this.otpRepo.insert({ phone, purpose, codeHash: hashOtp(phone, code), expiresAt });

    const templateCode = purpose === '2fa' ? 'SMS-2FA' : isResend ? 'SMS-OTP-RESEND' : 'SMS-OTP';
    await this.sms.send({ phone, templateCode, params: { code } });

    return { message: 'کد تأیید ارسال شد', expires_in: OTP_TTL_SECONDS, is_resend: isResend };
  }

  async verify(phone: string, code: string, purpose: string): Promise<OtpVerifyResult> {
    this.assertPhone(phone);
    this.assertCode(code);

    const otp = await this.otpRepo.latestActive(phone, purpose);
    if (!otp) {
      throw new ApiException(
        ErrorCode.OTP_EXPIRED,
        HttpStatus.BAD_REQUEST,
        'کد منقضی شده است. کد جدید درخواست کنید',
      );
    }

    if (otp.locked_until && otp.locked_until.getTime() > Date.now()) {
      const retryAfterSeconds = Math.max(
        1,
        Math.ceil((otp.locked_until.getTime() - Date.now()) / 1000),
      );
      throw new ApiException(
        ErrorCode.OTP_TRIES_EXCEEDED,
        HttpStatus.TOO_MANY_REQUESTS,
        'تلاش بعدی بعد از ۱۵ دقیقه',
        [{ retry_after_seconds: retryAfterSeconds }],
      );
    }

    if (otp.expires_at.getTime() <= Date.now()) {
      throw new ApiException(
        ErrorCode.OTP_EXPIRED,
        HttpStatus.BAD_REQUEST,
        'کد منقضی شده است. کد جدید درخواست کنید',
      );
    }

    if (!verifyOtpHash(phone, code, otp.code_hash)) {
      const attempts = otp.attempts + 1;
      await this.otpRepo.setAttempts(otp.id, attempts);
      if (attempts >= OTP_MAX_ATTEMPTS) {
        await this.otpRepo.lock(otp.id, new Date(Date.now() + OTP_LOCK_SECONDS * 1000));
        throw new ApiException(
          ErrorCode.OTP_TRIES_EXCEEDED,
          HttpStatus.TOO_MANY_REQUESTS,
          'تلاش بعدی بعد از ۱۵ دقیقه',
          [{ retry_after_seconds: OTP_LOCK_SECONDS }],
        );
      }
      const remaining = OTP_MAX_ATTEMPTS - attempts;
      throw new ApiException(
        ErrorCode.OTP_INVALID,
        HttpStatus.BAD_REQUEST,
        `کد اشتباه است. ${toPersianDigits(remaining)} تلاش دیگر دارید`,
        [{ remaining_attempts: remaining }],
      );
    }

    await this.otpRepo.consume(otp.id);

    let user = await this.userRepo.findByPhone(phone);
    let isNewUser = false;
    if (!user) {
      user = await this.userRepo.create(phone);
      await this.userRepo.assignRole(user.id, 'customer', null);
      isNewUser = true;
    }
    return { userId: user.id, isNewUser, user };
  }
}
