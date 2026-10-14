import { HttpStatus, Inject, Injectable } from '@nestjs/common';
import { ErrorCode } from '../../common/error-codes';
import { ApiException } from '../../common/exceptions/api.exception';
import { Paginated } from '../../common/pagination/pagination';
import { SMS_PROVIDER } from '../../providers/sms/sms-provider';
import type { SmsProvider } from '../../providers/sms/sms-provider';
import { isKnownRole, pickPrimaryRole } from './auth.roles';
import { IssuedTokens } from './auth.types';
import { OtpService } from './otp.service';
import { AuditRepository } from './repositories/audit.repository';
import { SessionRepository } from './repositories/session.repository';
import { UserRow, UserRepository } from './repositories/user.repository';
import { SessionService } from './session.service';
import { ADMIN_SHORT_TTL_ROLES, TokenService } from './token.service';

/** زمینه درخواست برای ثبت نشست/لاگ. */
export interface RequestContext {
  ip?: string | null;
  userAgent?: string | null;
  deviceId?: string | null;
  platform?: string | null;
  requestId?: string | null;
}

export interface PublicUser {
  id: string;
  phone: string;
  full_name: string | null;
  role: string;
  roles: string[];
  status: string;
  terms_version: string | null;
  /** اگر `PENDING_DELETION` باشد، مهلت انصراف (M-01.5). */
  deletion_pending_until: string | null;
}

function publicUser(user: UserRow, roles: string[], role: string): PublicUser {
  return {
    id: user.id,
    phone: user.phone,
    full_name: user.full_name,
    role,
    roles,
    status: user.status,
    terms_version: user.terms_version,
    deletion_pending_until: user.deletion_scheduled_at
      ? new Date(user.deletion_scheduled_at).toISOString()
      : null,
  };
}

/**
 * هماهنگ‌کننده Auth (SP-01): OTP → کاربر → نشست/توکن → پروفایل → نقش.
 * منطق OTP در `OtpService`، نشست/چرخش در `SessionService` است.
 */
@Injectable()
export class AuthService {
  constructor(
    private readonly otp: OtpService,
    private readonly users: UserRepository,
    private readonly sessions: SessionService,
    private readonly sessionRepo: SessionRepository,
    private readonly tokens: TokenService,
    private readonly audit: AuditRepository,
    @Inject(SMS_PROVIDER) private readonly sms: SmsProvider,
  ) {}

  requestOtp(
    phone: string,
    purpose: string,
    ip: string | null,
  ): Promise<{ message: string; expires_in: number; is_resend: boolean }> {
    return this.otp.request(phone, purpose, ip);
  }

  /** ورود با OTP → صدور JWT/Refresh (مشتری/فروشنده/ارائه‌دهنده). ادمین مالی/Super نیازمند 2FA است. */
  async verifyOtp(
    phone: string,
    code: string,
    ctx: RequestContext,
  ): Promise<IssuedTokens & { is_new_user: boolean; user: PublicUser }> {
    const { isNewUser, user } = await this.otp.verify(phone, code, 'login');
    this.assertLoginAllowed(user);

    const roles = await this.users.roles(user.id);
    const role = pickPrimaryRole(roles);
    if (ADMIN_SHORT_TTL_ROLES.has(role)) {
      // M-01.4: ادمین مالی/Super باید مسیر 2FA را ادامه دهد (POST /admin/auth/2fa/verify)
      throw new ApiException(
        ErrorCode.TWO_FA_REQUIRED,
        HttpStatus.UNAUTHORIZED,
        'کد ورود ادمین AMPET را وارد کنید',
      );
    }

    const { tokens, newDevice } = await this.sessions.startSession({
      userId: user.id,
      role,
      meta: {
        deviceId: ctx.deviceId,
        platform: ctx.platform,
        userAgent: ctx.userAgent,
        ip: ctx.ip,
      },
    });

    if (isNewUser) {
      await this.sms.send({ phone, templateCode: 'SMS-REGISTER', params: {} });
    } else if (newDevice && ctx.deviceId) {
      await this.sms.send({
        phone,
        templateCode: 'SMS-NEW-DEVICE',
        params: { device: ctx.platform ?? 'نامشخص' },
      });
    }
    await this.users.touchLastSeen(user.id);

    return { ...tokens, is_new_user: isNewUser, user: publicUser(user, roles, role) };
  }

  /** تأیید 2FA ادمین (M-01.4 skeleton) — صدور JWT ادمین ۱۰ دقیقه. */
  async verifyAdmin2fa(
    phone: string,
    code: string,
    ctx: RequestContext,
  ): Promise<IssuedTokens & { user: PublicUser }> {
    const { user } = await this.otp.verify(phone, code, '2fa');
    this.assertLoginAllowed(user);
    const roles = await this.users.roles(user.id);
    const role = pickPrimaryRole(roles);
    if (!ADMIN_SHORT_TTL_ROLES.has(role)) {
      throw new ApiException(ErrorCode.FORBIDDEN_ROLE, HttpStatus.FORBIDDEN, 'سطح دسترسی ناکافی');
    }
    const { tokens } = await this.sessions.startSession({
      userId: user.id,
      role,
      meta: {
        deviceId: ctx.deviceId,
        platform: ctx.platform,
        userAgent: ctx.userAgent,
        ip: ctx.ip,
      },
    });
    await this.users.touchLastSeen(user.id);
    return { ...tokens, user: publicUser(user, roles, role) };
  }

  /** چرخش refresh ۳۰ روزه؛ استفاده مجدد از توکن کهنه ⇒ ابطال کل دستگاه + ثبت رویداد. */
  async refresh(refreshToken: string, ctx: RequestContext): Promise<IssuedTokens> {
    let sid: string;
    try {
      sid = (await this.tokens.verifyRefresh(refreshToken)).sid;
    } catch {
      throw new ApiException(
        ErrorCode.TOKEN_EXPIRED,
        HttpStatus.UNAUTHORIZED,
        'نشست شما پایان یافت؛ برای امنیت بیشتر دوباره وارد شوید',
      );
    }

    const session = await this.sessions.findSession(sid);
    if (!session || session.revoked_at || session.deleted_at) {
      throw new ApiException(
        ErrorCode.TOKEN_INVALID,
        HttpStatus.UNAUTHORIZED,
        'نشست شما معتبر نیست؛ دوباره وارد شوید',
      );
    }

    if (session.refresh_hash !== this.sessions.hashRefresh(refreshToken)) {
      // سوءاستفاده: توکن کهنه پس از چرخش → ابطال همه نشست‌های کاربر
      await this.sessions.revokeAllForUser(session.user_id);
      await this.audit.record({
        actorId: session.user_id,
        action: 'auth.refresh_reuse',
        entityType: 'session',
        entityId: session.id,
        ip: ctx.ip ?? null,
        requestId: ctx.requestId ?? null,
      });
      throw new ApiException(
        ErrorCode.TOKEN_INVALID,
        HttpStatus.UNAUTHORIZED,
        'نشست شما معتبر نیست؛ دوباره وارد شوید',
      );
    }

    const user = await this.users.findById(session.user_id);
    if (!user) {
      throw new ApiException(ErrorCode.TOKEN_INVALID, HttpStatus.UNAUTHORIZED, 'کاربر یافت نشد');
    }
    this.assertLoginAllowed(user);
    const roles = await this.users.roles(user.id);
    return this.sessions.rotate(session, user.id, pickPrimaryRole(roles));
  }

  /** خروج — باطل کردن refresh همان نشست (بدون خطا اگر نامعتبر باشد). */
  async logout(refreshToken: string | undefined): Promise<{ message: string }> {
    if (refreshToken) {
      try {
        const { sid } = await this.tokens.verifyRefresh(refreshToken);
        await this.sessions.revoke(sid);
      } catch {
        /* توکن نامعتبر/باطل — همان پاسخ موفق */
      }
    }
    return { message: 'نشست باطل شد' };
  }

  /** پروفایل کاربر جاری. */
  async me(userId: string): Promise<PublicUser> {
    const user = await this.users.findById(userId);
    if (!user) throw ApiException.notFound('کاربر یافت نشد');
    const roles = await this.users.roles(userId);
    return publicUser(user, roles, pickPrimaryRole(roles));
  }

  /** تکمیل/ویرایش پروفایل — نام الزامی در اولین تکمیل + پذیرش قوانین. */
  async patchMe(
    userId: string,
    dto: { full_name?: string; first_name?: string; last_name?: string; terms_version?: string },
  ): Promise<PublicUser> {
    const user = await this.users.findById(userId);
    if (!user) throw ApiException.notFound('کاربر یافت نشد');

    const fullName =
      dto.full_name ?? [dto.first_name, dto.last_name].filter(Boolean).join(' ').trim() ?? '';
    const isFirstCompletion = !user.full_name;

    if (isFirstCompletion) {
      const accepted = dto.terms_version ? true : await this.users.hasAcceptedTerms(userId);
      if (!accepted) {
        throw new ApiException(
          ErrorCode.TERMS_NOT_ACCEPTED,
          HttpStatus.UNPROCESSABLE_ENTITY,
          'برای ادامه باید قوانین را بپذیرید',
        );
      }
    }

    if (dto.terms_version) {
      await this.users.recordTermsAcceptance(userId, dto.terms_version);
      await this.users.setTermsVersion(userId, dto.terms_version);
    }
    if (fullName) {
      await this.users.updateProfile(userId, fullName);
    }

    const fresh = await this.users.findById(userId);
    if (!fresh) throw ApiException.notFound('کاربر یافت نشد');
    const roles = await this.users.roles(userId);
    return publicUser(fresh, roles, pickPrimaryRole(roles));
  }

  /** تغییر نقش (ادمین) — ثبت before/after + ابطال نشست‌های فعال کاربر (M-01.4). */
  async changeRole(
    actorId: string,
    targetUserId: string,
    newRole: string,
    ctx: RequestContext,
  ): Promise<{ message: string; revoked_sessions: number }> {
    if (!isKnownRole(newRole)) {
      throw ApiException.validation('نقش نامعتبر است', [{ field: 'role' }]);
    }
    const target = await this.users.findById(targetUserId);
    if (!target) throw ApiException.notFound('کاربر یافت نشد');

    const before = await this.users.roles(targetUserId);
    if (!before.includes(newRole)) {
      await this.users.assignRole(targetUserId, newRole, actorId);
    }
    const after = await this.users.roles(targetUserId);

    await this.audit.record({
      actorId,
      action: 'admin.user_role_change',
      entityType: 'user',
      entityId: targetUserId,
      before: { roles: before },
      after: { roles: after },
      ip: ctx.ip ?? null,
      requestId: ctx.requestId ?? null,
    });

    const revoked = await this.sessions.revokeAllForUser(targetUserId);
    return { message: 'نقش تغییر کرد و نشست‌های فعال باطل شدند', revoked_sessions: revoked };
  }

  /** نشست‌های فعال کاربر جاری (با علامت «این دستگاه»). */
  async listSessions(userId: string, currentSid: string): Promise<Paginated<unknown>> {
    const rows = await this.sessions.listActive(userId);
    const items = rows.map((s) => ({
      id: s.id,
      device: s.device_id ?? 'نامشخص',
      platform: s.platform ?? 'نامشخص',
      last_active_at: new Date(s.updated_at).toISOString(),
      created_at: new Date(s.created_at).toISOString(),
      current: s.id === currentSid,
    }));
    return { items, meta: { page: 1, per_page: 50, next_cursor: null, total: items.length } };
  }

  async revokeSession(userId: string, sessionId: string): Promise<{ message: string }> {
    const session = await this.sessions.findActiveForUser(sessionId, userId);
    if (!session) throw ApiException.notFound('نشست یافت نشد');
    await this.sessionRepo.revoke(sessionId);
    return { message: 'نشست باطل شد' };
  }

  async revokeAllSessions(
    userId: string,
    currentSid: string | null,
  ): Promise<{ message: string; revoked_sessions: number }> {
    const count = await this.sessions.revokeAllForUser(userId, currentSid ?? undefined);
    return { message: 'خروج از همه دستگاه‌ها انجام شد', revoked_sessions: count };
  }

  private assertLoginAllowed(user: UserRow): void {
    if (!user.is_active || user.status === 'SUSPENDED') {
      throw new ApiException(
        ErrorCode.ACCOUNT_BLOCKED,
        HttpStatus.FORBIDDEN,
        'امکان ورود برای این شماره وجود ندارد',
      );
    }
  }
}
