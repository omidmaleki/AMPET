import { Injectable } from '@nestjs/common';
import { createHash } from 'crypto';
import { IssuedTokens } from './auth.types';
import { SessionRepository, SessionRow } from './repositories/session.repository';
import { REFRESH_TTL_SECONDS, TokenService } from './token.service';

/** فراداده دستگاه/شبکه در زمان ورود (SP-01 M-01.3). */
export interface SessionMeta {
  deviceId?: string | null;
  platform?: string | null;
  userAgent?: string | null;
  ip?: string | null;
}

/**
 * مدیریت نشست و refresh چرخشی (SP-01 M-01.3):
 * - refresh ۳۰ روزه؛ فقط **هش** در `sessions.refresh_hash` ذخیره می‌شود
 * - هر چرخش، هش را جایگزین می‌کند ⇒ استفاده مجدد از توکن کهنه قابل تشخیص است
 * - تشخیص دستگاه جدید قبل از ساخت نشست (برای `SMS-NEW-DEVICE`)
 */
@Injectable()
export class SessionService {
  constructor(
    private readonly sessions: SessionRepository,
    private readonly tokens: TokenService,
  ) {}

  hashRefresh(token: string): string {
    return createHash('sha256').update(token).digest('hex');
  }

  private refreshExpiry(): Date {
    return new Date(Date.now() + REFRESH_TTL_SECONDS * 1000);
  }

  private async issueTokens(
    sid: string,
    userId: string,
    role: string,
    expiresAt: Date,
  ): Promise<IssuedTokens> {
    const refreshToken = await this.tokens.signRefresh(sid);
    await this.sessions.rotate(sid, this.hashRefresh(refreshToken), expiresAt);
    const accessToken = await this.tokens.signAccess({ id: userId, role, sid });
    return {
      access_token: accessToken,
      refresh_token: refreshToken,
      expires_in: this.tokens.accessTtlSeconds(role),
    };
  }

  /** شروع نشست پس از ورود موفق. `newDevice` باید پیش از ساخت نشست سنجیده شود. */
  async startSession(params: {
    userId: string;
    role: string;
    meta: SessionMeta;
  }): Promise<{ tokens: IssuedTokens; sid: string; newDevice: boolean }> {
    const { userId, role, meta } = params;
    const deviceId = meta.deviceId ?? null;
    const newDevice = deviceId ? !(await this.sessions.hasActiveDevice(userId, deviceId)) : false;

    const expiresAt = this.refreshExpiry();
    const session = await this.sessions.create({
      userId,
      refreshHash: 'pending',
      deviceId,
      platform: meta.platform ?? null,
      userAgent: meta.userAgent ?? null,
      ip: meta.ip ?? null,
      expiresAt,
    });
    const tokens = await this.issueTokens(session.id, userId, role, expiresAt);
    return { tokens, sid: session.id, newDevice };
  }

  /** چرخش refresh روی همان نشست. */
  rotate(session: SessionRow, userId: string, role: string): Promise<IssuedTokens> {
    return this.issueTokens(session.id, userId, role, this.refreshExpiry());
  }

  findSession(id: string): Promise<SessionRow | null> {
    return this.sessions.findById(id);
  }

  findActiveByIdAndHash(id: string, refreshToken: string): Promise<SessionRow | null> {
    return this.sessions.findActiveByIdAndHash(id, this.hashRefresh(refreshToken));
  }

  async revoke(sessionId: string): Promise<void> {
    await this.sessions.revoke(sessionId);
  }

  revokeAllForUser(userId: string, exceptId?: string): Promise<number> {
    return this.sessions.revokeAllForUser(userId, exceptId);
  }

  findActiveForUser(sessionId: string, userId: string): Promise<SessionRow | null> {
    return this.sessions.findActiveByIdForUser(sessionId, userId);
  }

  listActive(userId: string): Promise<SessionRow[]> {
    return this.sessions.listActive(userId);
  }
}
