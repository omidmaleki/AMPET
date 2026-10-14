import { Inject, Injectable, OnModuleDestroy } from '@nestjs/common';
import { Pool, PoolClient, QueryResult, QueryResultRow } from 'pg';
import { PG_POOL } from './database.constants';

/** پارامترهای کوئری — فقط مقادیر binding، نه رشته SQL. */
export type SqlParams = ReadonlyArray<unknown>;

/**
 * پوشش نازک روی `pg.Pool` — تنها راه دسترسی ماژول‌ها به Postgres
 * (بدون ORM؛ طبق PLAN §۱ «مونولیت ماژولار، SQL مهاجرت دستی»).
 * - `transaction` تضمین BEGIN/COMMIT/ROLLBACK + release
 * - بدون query، اتصالی باز نمی‌شود ⇒ بوت اپ بدون Postgres ممکن است (تست‌های SP-00)
 */
@Injectable()
export class DatabaseService implements OnModuleDestroy {
  constructor(@Inject(PG_POOL) private readonly pool: Pool) {}

  query<R extends QueryResultRow = QueryResultRow>(
    text: string,
    params: SqlParams = [],
  ): Promise<QueryResult<R>> {
    return this.pool.query<R>(text, params as unknown[]);
  }

  /** یک‌ردیفی؛ در نبود ردیف `null`. */
  async one<R extends QueryResultRow = QueryResultRow>(
    text: string,
    params: SqlParams = [],
  ): Promise<R | null> {
    const res = await this.query<R>(text, params);
    return res.rows[0] ?? null;
  }

  /** چندردیفی. */
  async many<R extends QueryResultRow = QueryResultRow>(
    text: string,
    params: SqlParams = [],
  ): Promise<R[]> {
    const res = await this.query<R>(text, params);
    return res.rows;
  }

  /** اجرای اتمیک؛ خطا → ROLLBACK و پرتاب مجدد. */
  async transaction<T>(fn: (client: PoolClient) => Promise<T>): Promise<T> {
    const client = await this.pool.connect();
    try {
      await client.query('BEGIN');
      const out = await fn(client);
      await client.query('COMMIT');
      return out;
    } catch (err) {
      await client.query('ROLLBACK').catch(() => undefined);
      throw err;
    } finally {
      client.release();
    }
  }

  async onModuleDestroy(): Promise<void> {
    await this.pool.end().catch(() => undefined);
  }
}
