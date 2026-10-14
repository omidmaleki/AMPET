import { Injectable } from '@nestjs/common';
import { DatabaseService } from '../../../database/database.service';

/**
 * audit_logs فقط‌افزودنی (SP-01 M-01.4؛ تریگر DB هر UPDATE/DELETE را رد می‌کند).
 */
@Injectable()
export class AuditRepository {
  constructor(private readonly db: DatabaseService) {}

  async record(params: {
    actorId: string | null;
    action: string;
    entityType: string;
    entityId?: string | null;
    before?: unknown;
    after?: unknown;
    ip?: string | null;
    requestId?: string | null;
  }): Promise<void> {
    await this.db.query(
      `INSERT INTO audit_logs
         (actor_id, action, entity_type, entity_id, before_data, after_data, ip, request_id)
       VALUES ($1, $2, $3, $4, $5, $6, $7, $8)`,
      [
        params.actorId,
        params.action,
        params.entityType,
        params.entityId ?? null,
        params.before === undefined ? null : JSON.stringify(params.before),
        params.after === undefined ? null : JSON.stringify(params.after),
        params.ip ?? null,
        params.requestId ?? null,
      ],
    );
  }
}
