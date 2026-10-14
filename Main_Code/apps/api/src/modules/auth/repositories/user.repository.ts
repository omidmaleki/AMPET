import { Injectable } from '@nestjs/common';
import { DatabaseService } from '../../../database/database.service';

export type UserRow = {
  id: string;
  phone: string;
  full_name: string | null;
  is_active: boolean;
  status: string;
  two_factor_enabled: boolean;
  terms_version: string | null;
  deletion_scheduled_at: Date | null;
  last_seen_at: Date | null;
  created_at: Date;
  updated_at: Date;
  deleted_at: Date | null;
};

/** دسترسی داده کاربر (SP-01). نقش‌ها فقط از `user_roles` می‌آیند. */
@Injectable()
export class UserRepository {
  constructor(private readonly db: DatabaseService) {}

  findByPhone(phone: string): Promise<UserRow | null> {
    return this.db.one<UserRow>(`SELECT * FROM users WHERE phone = $1 AND deleted_at IS NULL`, [
      phone,
    ]);
  }

  findById(id: string): Promise<UserRow | null> {
    return this.db.one<UserRow>(`SELECT * FROM users WHERE id = $1 AND deleted_at IS NULL`, [id]);
  }

  async create(phone: string): Promise<UserRow> {
    const row = await this.db.one<UserRow>(`INSERT INTO users (phone) VALUES ($1) RETURNING *`, [
      phone,
    ]);
    if (!row) throw new Error('ساخت کاربر ناموفق بود');
    return row;
  }

  roles(userId: string): Promise<string[]> {
    return this.db
      .many<{ role: string }>(
        `SELECT role FROM user_roles WHERE user_id = $1 AND deleted_at IS NULL ORDER BY created_at`,
        [userId],
      )
      .then((rows) => rows.map((r) => r.role));
  }

  async hasRole(userId: string, role: string): Promise<boolean> {
    const row = await this.db.one(
      `SELECT 1 AS ok FROM user_roles WHERE user_id = $1 AND role = $2 AND deleted_at IS NULL`,
      [userId, role],
    );
    return row !== null;
  }

  async assignRole(userId: string, role: string, grantedBy: string | null): Promise<void> {
    await this.db.query(
      `INSERT INTO user_roles (user_id, role, granted_by) VALUES ($1, $2, $3)
       ON CONFLICT (user_id, role) WHERE deleted_at IS NULL DO NOTHING`,
      [userId, role, grantedBy],
    );
  }

  async setStatus(userId: string, status: string): Promise<void> {
    await this.db.query(`UPDATE users SET status = $2, updated_at = now() WHERE id = $1`, [
      userId,
      status,
    ]);
  }

  async updateProfile(userId: string, fullName: string): Promise<void> {
    await this.db.query(`UPDATE users SET full_name = $2, updated_at = now() WHERE id = $1`, [
      userId,
      fullName,
    ]);
  }

  async setTermsVersion(userId: string, version: string): Promise<void> {
    await this.db.query(`UPDATE users SET terms_version = $2, updated_at = now() WHERE id = $1`, [
      userId,
      version,
    ]);
  }

  async touchLastSeen(userId: string): Promise<void> {
    await this.db.query(`UPDATE users SET last_seen_at = now() WHERE id = $1`, [userId]);
  }

  async hasAcceptedTerms(userId: string, version?: string): Promise<boolean> {
    const row = version
      ? await this.db.one(
          `SELECT 1 AS ok FROM terms_acceptances
            WHERE user_id = $1 AND terms_version = $2 AND deleted_at IS NULL LIMIT 1`,
          [userId, version],
        )
      : await this.db.one(
          `SELECT 1 AS ok FROM terms_acceptances
            WHERE user_id = $1 AND deleted_at IS NULL LIMIT 1`,
          [userId],
        );
    return row !== null;
  }

  async recordTermsAcceptance(userId: string, version: string): Promise<void> {
    await this.db.query(
      `INSERT INTO terms_acceptances (user_id, terms_version) VALUES ($1, $2)
       ON CONFLICT (user_id, terms_version) WHERE deleted_at IS NULL DO NOTHING`,
      [userId, version],
    );
  }

  /** لیست همه مجوزهای مؤثر کاربر از طریق نقش‌هایش (RBAC). */
  permissions(userId: string): Promise<string[]> {
    return this.db
      .many<{ permission_code: string }>(
        `SELECT DISTINCT rp.permission_code
           FROM user_roles ur
           JOIN role_permissions rp ON rp.role = ur.role AND rp.deleted_at IS NULL
          WHERE ur.user_id = $1 AND ur.deleted_at IS NULL`,
        [userId],
      )
      .then((rows) => rows.map((r) => r.permission_code));
  }
}
