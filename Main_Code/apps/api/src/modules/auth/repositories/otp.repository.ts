import { Injectable } from '@nestjs/common';
import { DatabaseService } from '../../../database/database.service';

export type OtpRow = {
  id: string;
  phone: string;
  purpose: string;
  code_hash: string;
  attempts: number;
  expires_at: Date;
  locked_until: Date | null;
  created_at: Date;
  deleted_at: Date | null;
};

/** دسترسی داده کد یک‌بارمصرف (SP-01 M-01.2). فقط هش ذخیره می‌شود. */
@Injectable()
export class OtpRepository {
  constructor(private readonly db: DatabaseService) {}

  /** آخرین کد فعال (استفاده‌نشده) برای شماره+هدف. */
  latestActive(phone: string, purpose: string): Promise<OtpRow | null> {
    return this.db.one<OtpRow>(
      `SELECT * FROM otp_codes
        WHERE phone = $1 AND purpose = $2 AND deleted_at IS NULL
        ORDER BY created_at DESC LIMIT 1`,
      [phone, purpose],
    );
  }

  async insert(params: {
    phone: string;
    purpose: string;
    codeHash: string;
    expiresAt: Date;
  }): Promise<OtpRow> {
    const row = await this.db.one<OtpRow>(
      `INSERT INTO otp_codes (phone, purpose, code_hash, expires_at)
       VALUES ($1, $2, $3, $4) RETURNING *`,
      [params.phone, params.purpose, params.codeHash, params.expiresAt],
    );
    if (!row) throw new Error('درج کد تأیید ناموفق بود');
    return row;
  }

  /** باطل‌سازی همه کدهای فعال یک شماره/هدف (ارسال مجدد یا مصرف). */
  async invalidateActive(phone: string, purpose: string): Promise<void> {
    await this.db.query(
      `UPDATE otp_codes SET deleted_at = now()
        WHERE phone = $1 AND purpose = $2 AND deleted_at IS NULL`,
      [phone, purpose],
    );
  }

  async setAttempts(id: string, attempts: number): Promise<void> {
    await this.db.query(`UPDATE otp_codes SET attempts = $2 WHERE id = $1`, [id, attempts]);
  }

  async lock(id: string, lockedUntil: Date): Promise<void> {
    await this.db.query(`UPDATE otp_codes SET locked_until = $2 WHERE id = $1`, [id, lockedUntil]);
  }

  /** مصرف (علامت‌گذاری استفاده‌شده) — soft-delete. */
  async consume(id: string): Promise<void> {
    await this.db.query(`UPDATE otp_codes SET deleted_at = now() WHERE id = $1`, [id]);
  }
}
