import { Injectable } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { JwtService } from '@nestjs/jwt';
import { randomUUID } from 'crypto';
import { AccessClaims, AuthUser, RefreshClaims } from './auth.types';

/** نقش‌هایی که Access کوتاه (۱۰ دقیقه) می‌گیرند (SP-01 M-01.3 — ادمین مالی/Super). */
export const ADMIN_SHORT_TTL_ROLES = new Set(['admin_super', 'accountant', 'finance']);

export const ACCESS_TTL_CUSTOMER_SECONDS = 900; // ۱۵ دقیقه
export const ACCESS_TTL_ADMIN_SECONDS = 600; // ۱۰ دقیقه
export const REFRESH_TTL_SECONDS = 30 * 24 * 60 * 60; // ۳۰ روز

/**
 * صدور/تأیید توکن (SP-01 M-01.3) — دو راز جدا:
 * - Access: ۱۵ دقیقه (ادمین ۱۰)
 * - Refresh: ۳۰ روزه چرخشی (hash در sessions)
 */
@Injectable()
export class TokenService {
  constructor(
    private readonly jwt: JwtService,
    private readonly config: ConfigService,
  ) {}

  private get accessSecret(): string {
    return this.config.get<string>('JWT_ACCESS_SECRET', 'change_me_access_32chars_min');
  }

  private get refreshSecret(): string {
    return this.config.get<string>('JWT_REFRESH_SECRET', 'change_me_refresh_32chars_min');
  }

  /** ثانیه‌ی عمر Access بر اساس نقش. */
  accessTtlSeconds(role: string): number {
    return ADMIN_SHORT_TTL_ROLES.has(role) ? ACCESS_TTL_ADMIN_SECONDS : ACCESS_TTL_CUSTOMER_SECONDS;
  }

  async signAccess(user: AuthUser): Promise<string> {
    const ttl = this.accessTtlSeconds(user.role);
    const claims: AccessClaims = { sub: user.id, role: user.role, sid: user.sid };
    return this.jwt.signAsync(claims, { secret: this.accessSecret, expiresIn: ttl });
  }

  async signRefresh(sid: string): Promise<string> {
    const claims: RefreshClaims = { sid, type: 'refresh', jti: randomUUID() };
    return this.jwt.signAsync(claims, {
      secret: this.refreshSecret,
      expiresIn: REFRESH_TTL_SECONDS,
    });
  }

  async verifyAccess(token: string): Promise<AccessClaims> {
    return this.jwt.verifyAsync<AccessClaims>(token, { secret: this.accessSecret });
  }

  async verifyRefresh(token: string): Promise<RefreshClaims> {
    const claims = await this.jwt.verifyAsync<RefreshClaims>(token, {
      secret: this.refreshSecret,
    });
    if (claims.type !== 'refresh') throw new Error('نوع توکن نامعتبر است');
    return claims;
  }
}
