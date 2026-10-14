import { Injectable } from '@nestjs/common';
import { DatabaseService } from '../../../database/database.service';

export type SessionRow = {
  id: string;
  user_id: string;
  refresh_hash: string;
  device_id: string | null;
  platform: string | null;
  user_agent: string | null;
  ip: string | null;
  expires_at: Date;
  revoked_at: Date | null;
  created_at: Date;
  updated_at: Date;
  deleted_at: Date | null;
};

/** دسترسی داده نشست (SP-01 M-01.3) — refresh چرخشی با hash. */
@Injectable()
export class SessionRepository {
  constructor(private readonly db: DatabaseService) {}

  async create(params: {
    userId: string;
    refreshHash: string;
    deviceId: string | null;
    platform: string | null;
    userAgent: string | null;
    ip: string | null;
    expiresAt: Date;
  }): Promise<SessionRow> {
    const row = await this.db.one<SessionRow>(
      `INSERT INTO sessions (user_id, refresh_hash, device_id, platform, user_agent, ip, expires_at)
       VALUES ($1, $2, $3, $4, $5, $6, $7) RETURNING *`,
      [
        params.userId,
        params.refreshHash,
        params.deviceId,
        params.platform,
        params.userAgent,
        params.ip,
        params.expiresAt,
      ],
    );
    if (!row) throw new Error('ساخت نشست ناموفق بود');
    return row;
  }

  findById(id: string): Promise<SessionRow | null> {
    return this.db.one<SessionRow>(`SELECT * FROM sessions WHERE id = $1`, [id]);
  }

  /** نشست فعال معتبر بر اساس id + هش refresh (چرخش/ابطال). */
  findActiveByIdAndHash(id: string, refreshHash: string): Promise<SessionRow | null> {
    return this.db.one<SessionRow>(
      `SELECT * FROM sessions
        WHERE id = $1 AND refresh_hash = $2 AND revoked_at IS NULL
          AND deleted_at IS NULL AND expires_at > now()`,
      [id, refreshHash],
    );
  }

  findActiveByIdForUser(id: string, userId: string): Promise<SessionRow | null> {
    return this.db.one<SessionRow>(
      `SELECT * FROM sessions
        WHERE id = $1 AND user_id = $2 AND revoked_at IS NULL AND deleted_at IS NULL`,
      [id, userId],
    );
  }

  async rotate(id: string, newHash: string, newExpiry: Date): Promise<void> {
    await this.db.query(
      `UPDATE sessions SET refresh_hash = $2, expires_at = $3, updated_at = now() WHERE id = $1`,
      [id, newHash, newExpiry],
    );
  }

  async revoke(id: string): Promise<void> {
    await this.db.query(
      `UPDATE sessions SET revoked_at = now(), updated_at = now() WHERE id = $1 AND revoked_at IS NULL`,
      [id],
    );
  }

  /** ابطال همه نشست‌های فعال کاربر؛ `exceptId` می‌تواند نشست جاری را نگه دارد. */
  async revokeAllForUser(userId: string, exceptId?: string): Promise<number> {
    const res = await this.db.query(
      `UPDATE sessions SET revoked_at = now(), updated_at = now()
        WHERE user_id = $1 AND revoked_at IS NULL AND deleted_at IS NULL
          AND ($2::uuid IS NULL OR id <> $2::uuid)`,
      [userId, exceptId ?? null],
    );
    return res.rowCount ?? 0;
  }

  listActive(userId: string): Promise<SessionRow[]> {
    return this.db.many<SessionRow>(
      `SELECT * FROM sessions
        WHERE user_id = $1 AND revoked_at IS NULL AND deleted_at IS NULL AND expires_at > now()
        ORDER BY updated_at DESC`,
      [userId],
    );
  }

  /** شمار نشست‌های فعال یک دستگاه (برای تشخیص دستگاه جدید). */
  async hasActiveDevice(userId: string, deviceId: string): Promise<boolean> {
    const row = await this.db.one(
      `SELECT 1 AS ok FROM sessions
        WHERE user_id = $1 AND device_id = $2 AND revoked_at IS NULL
          AND deleted_at IS NULL AND expires_at > now() LIMIT 1`,
      [userId, deviceId],
    );
    return row !== null;
  }
}
