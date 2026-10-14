import { MemoryRateLimiter } from '../../src/common/rate-limit/rate-limiter.service';
import { ErrorCode } from '../../src/common/error-codes';
import { OtpService } from '../../src/modules/auth/otp.service';
import { OtpRepository } from '../../src/modules/auth/repositories/otp.repository';
import { UserRepository, UserRow } from '../../src/modules/auth/repositories/user.repository';
import type { SmsProvider, SmsResult, SmsSendParams } from '../../src/providers/sms/sms-provider';

/** ردیف OTP در حافظه. */
interface FakeOtp {
  id: string;
  phone: string;
  purpose: string;
  code_hash: string;
  attempts: number;
  expires_at: Date;
  locked_until: Date | null;
  created_at: Date;
  deleted_at: Date | null;
}

class FakeOtpRepo {
  rows: FakeOtp[] = [];
  private seq = 0;

  async latestActive(phone: string, purpose: string): Promise<FakeOtp | null> {
    const list = this.rows
      .filter((r) => r.phone === phone && r.purpose === purpose && r.deleted_at === null)
      .sort((a, b) => b.created_at.getTime() - a.created_at.getTime());
    return list[0] ?? null;
  }

  async insert(p: {
    phone: string;
    purpose: string;
    codeHash: string;
    expiresAt: Date;
  }): Promise<FakeOtp> {
    this.seq += 1;
    const row: FakeOtp = {
      id: `otp-${this.seq}`,
      phone: p.phone,
      purpose: p.purpose,
      code_hash: p.codeHash,
      attempts: 0,
      expires_at: p.expiresAt,
      locked_until: null,
      created_at: new Date(),
      deleted_at: null,
    };
    this.rows.push(row);
    return row;
  }

  async invalidateActive(phone: string, purpose: string): Promise<void> {
    for (const r of this.rows) {
      if (r.phone === phone && r.purpose === purpose && r.deleted_at === null)
        r.deleted_at = new Date();
    }
  }

  async setAttempts(id: string, attempts: number): Promise<void> {
    const r = this.rows.find((x) => x.id === id);
    if (r) r.attempts = attempts;
  }

  async lock(id: string, lockedUntil: Date): Promise<void> {
    const r = this.rows.find((x) => x.id === id);
    if (r) r.locked_until = lockedUntil;
  }

  async consume(id: string): Promise<void> {
    const r = this.rows.find((x) => x.id === id);
    if (r) r.deleted_at = new Date();
  }
}

class FakeUserRepo {
  users: UserRow[] = [];
  rolesMap = new Map<string, string[]>();

  async findByPhone(phone: string): Promise<UserRow | null> {
    return this.users.find((u) => u.phone === phone && !u.deleted_at) ?? null;
  }

  async create(phone: string): Promise<UserRow> {
    const user: UserRow = {
      id: `user-${this.users.length + 1}`,
      phone,
      full_name: null,
      is_active: true,
      status: 'ACTIVE',
      two_factor_enabled: false,
      terms_version: null,
      deletion_scheduled_at: null,
      last_seen_at: null,
      created_at: new Date(),
      updated_at: new Date(),
      deleted_at: null,
    };
    this.users.push(user);
    return user;
  }

  async assignRole(userId: string, role: string): Promise<void> {
    const list = this.rolesMap.get(userId) ?? [];
    if (!list.includes(role)) list.push(role);
    this.rolesMap.set(userId, list);
  }
}

class FakeSms implements SmsProvider {
  sent: SmsSendParams[] = [];
  async sendOtp(): Promise<SmsResult> {
    return { messageId: 'm', success: true };
  }
  async send(params: SmsSendParams): Promise<SmsResult> {
    this.sent.push(params);
    return { messageId: 'm', success: true };
  }
}

function makeService(): {
  service: OtpService;
  otpRepo: FakeOtpRepo;
  userRepo: FakeUserRepo;
  sms: FakeSms;
} {
  const otpRepo = new FakeOtpRepo();
  const userRepo = new FakeUserRepo();
  const sms = new FakeSms();
  const limiter = new MemoryRateLimiter();
  const service = new OtpService(
    otpRepo as unknown as OtpRepository,
    userRepo as unknown as UserRepository,
    sms,
    limiter,
  );
  return { service, otpRepo, userRepo, sms };
}

const PHONE = '09121234567';
const IP = '5.5.5.5';

function wrongCode(real: string): string {
  return real === '00000' ? '11111' : '00000';
}

describe('OtpService (SP-01 M-01.2)', () => {
  it('otp_request_valid_returns_120s_and_stores_only_hash', async () => {
    const { service, otpRepo, sms } = makeService();
    const res = await service.request(PHONE, 'login', IP);
    expect(res.expires_in).toBe(120);
    expect(otpRepo.rows).toHaveLength(1);
    // فقط هش ذخیره می‌شود — متن کد در DB نیست
    const storedCode = sms.sent[0]?.params.code ?? '';
    expect(storedCode).toMatch(/^\d{5}$/);
    expect(otpRepo.rows[0].code_hash).not.toBe(storedCode);
  });

  it('otp_request_invalid_phone_uses_exact_fa_message', async () => {
    const { service } = makeService();
    await expect(service.request('12345', 'login', IP)).rejects.toMatchObject({
      code: ErrorCode.VALIDATION_ERROR,
      message: 'شماره موبایل معتبر نیست. ۱۱ رقم وارد کنید',
    });
  });

  it('otp_request_rate_limited_3_per_10min_per_phone_and_ip', async () => {
    const { service } = makeService();
    await service.request(PHONE, 'login', IP);
    await service.request(PHONE, 'login', IP);
    await service.request(PHONE, 'login', IP);
    await expect(service.request(PHONE, 'login', IP)).rejects.toMatchObject({
      code: ErrorCode.RATE_LIMIT_EXCEEDED,
    });
  });

  it('otp_resend_invalidates_previous_code', async () => {
    const { service, otpRepo, sms } = makeService();
    await service.request(PHONE, 'login', IP);
    const firstCode = sms.sent[0].params.code;
    const res = await service.request(PHONE, 'login', IP);
    expect(res.is_resend).toBe(true);
    // کد قبلی باطل شده و کد جدید فرق دارد
    const active = await otpRepo.latestActive(PHONE, 'login');
    expect(active?.code_hash).not.toBe(otpRepo.rows[0].code_hash);
    expect(otpRepo.rows[0].deleted_at).not.toBeNull();
    expect(firstCode).toBeDefined();
  });

  it('otp_wrong_code_counts_and_locks_15min_with_retry_after_900', async () => {
    const { service, sms } = makeService();
    await service.request(PHONE, 'login', IP);
    const bad = wrongCode(sms.sent[0].params.code);

    await expect(service.verify(PHONE, bad, 'login')).rejects.toMatchObject({
      code: ErrorCode.OTP_INVALID,
      message: 'کد اشتباه است. ۲ تلاش دیگر دارید',
    });
    await expect(service.verify(PHONE, bad, 'login')).rejects.toMatchObject({
      code: ErrorCode.OTP_INVALID,
      message: 'کد اشتباه است. ۱ تلاش دیگر دارید',
    });
    await expect(service.verify(PHONE, bad, 'login')).rejects.toMatchObject({
      code: ErrorCode.OTP_TRIES_EXCEEDED,
      details: [{ retry_after_seconds: 900 }],
    });
  });

  it('otp_expired_code_rejected', async () => {
    const { service, otpRepo, sms } = makeService();
    await service.request(PHONE, 'login', IP);
    const code = sms.sent[0].params.code;
    otpRepo.rows[0].expires_at = new Date(Date.now() - 1000);
    await expect(service.verify(PHONE, code, 'login')).rejects.toMatchObject({
      code: ErrorCode.OTP_EXPIRED,
      message: 'کد منقضی شده است. کد جدید درخواست کنید',
    });
  });

  it('otp_verify_success_creates_customer_and_consumes_code', async () => {
    const { service, otpRepo, userRepo, sms } = makeService();
    await service.request(PHONE, 'login', IP);
    const code = sms.sent[0].params.code;
    const result = await service.verify(PHONE, code, 'login');
    expect(result.isNewUser).toBe(true);
    expect(result.user.phone).toBe(PHONE);
    expect(userRepo.rolesMap.get(result.userId)).toEqual(['customer']);
    expect(otpRepo.rows[0].deleted_at).not.toBeNull();
  });

  it('otp_verify_locked_returns_retry_after', async () => {
    const { service, otpRepo, sms } = makeService();
    await service.request(PHONE, 'login', IP);
    const code = sms.sent[0].params.code;
    otpRepo.rows[0].locked_until = new Date(Date.now() + 900_000);
    await expect(service.verify(PHONE, code, 'login')).rejects.toMatchObject({
      code: ErrorCode.OTP_TRIES_EXCEEDED,
    });
  });

  it('otp_verify_existing_user_is_not_new', async () => {
    const { service, userRepo, sms } = makeService();
    await userRepo.create(PHONE); // کاربر از قبل
    await service.request(PHONE, 'login', IP);
    const code = sms.sent[0].params.code;
    const result = await service.verify(PHONE, code, 'login');
    expect(result.isNewUser).toBe(false);
  });
});
