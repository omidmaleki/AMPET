import { Global, Logger, Module, Provider } from '@nestjs/common';
import { Pool } from 'pg';
import { PG_POOL } from './database.constants';
import { DatabaseService } from './database.service';

function buildPool(): Pool {
  const connectionString =
    process.env.DATABASE_URL ??
    'postgresql://ampet:ampet_dev_password_change_me@localhost:5432/ampet_dev';
  const pool = new Pool({
    connectionString,
    max: Number(process.env.PG_POOL_MAX ?? 10),
    idleTimeoutMillis: 30_000,
    connectionTimeoutMillis: Number(process.env.PG_CONNECT_TIMEOUT_MS ?? 5_000),
  });
  // خطای کلاینت بی‌کار نباید پروسه را کرش کند (مثلاً Postgres خاموش در dev)
  pool.on('error', (err) => {
    new Logger('PgPool').error(`خطای اتصال بی‌کار: ${err.message}`);
  });
  return pool;
}

const poolProvider: Provider = { provide: PG_POOL, useFactory: buildPool };

/**
 * لایه دیتابیس سراسری (SP-01 / M-01.0). بدون ORM؛ استخر `pg`.
 * در دسترس همه ماژول‌های دامنه بدون import مجدد.
 */
@Global()
@Module({
  providers: [poolProvider, DatabaseService],
  exports: [PG_POOL, DatabaseService],
})
export class DatabaseModule {}
