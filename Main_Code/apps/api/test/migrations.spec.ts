import { Client } from 'pg';
// eslint-disable-next-line @typescript-eslint/no-var-requires
const migrate = require('../scripts/migrate.js');

/**
 * migrations/up_then_down_on_fresh_database (SP-00 §4 + ماده ۸.۵)
 * روی یک دیتابیس تازه و مجزا اجرا می‌شود تا به وضعیت dev وابسته نباشد.
 */
const dbUrl = process.env.DATABASE_URL;
const maybe = dbUrl ? describe : describe.skip;

maybe('Migrations — up/down on fresh database (SP-00 §4)', () => {
  it('migrations/up_then_down_on_fresh_database', async () => {
    const base = new URL(dbUrl as string);
    const dbName = `ampet_mig_${Date.now()}`;
    const adminUrl = new URL(base.toString());
    adminUrl.pathname = '/postgres';

    const admin = new Client({ connectionString: adminUrl.toString() });
    let adminConnected = false;
    try {
      await admin.connect();
      adminConnected = true;
    } catch (e) {
      if (process.env.CI === 'true') throw e;
      console.warn('migrations: DATABASE_URL در دسترس نیست — تست رد شد');
      return;
    }

    const testUrl = new URL(base.toString());
    testUrl.pathname = `/${dbName}`;
    const client = new Client({ connectionString: testUrl.toString() });

    try {
      await admin.query(`CREATE DATABASE ${dbName}`);
      await client.connect();

      const upCount = await migrate.runUp(client, { log: () => undefined });
      expect(upCount).toBe(8); // 001 + 002-user-auth (SP-01) + ۶ placeholder

      const users = await client.query(`SELECT to_regclass('public.users') AS t`);
      expect(users.rows[0].t).toBe('users');

      const tableCount = await client.query(
        `SELECT count(*)::int AS c FROM information_schema.tables WHERE table_schema = 'public'`,
      );
      expect(tableCount.rows[0].c).toBeGreaterThanOrEqual(6); // ۵ جدول + schema_migrations

      const applied = await client.query(`SELECT count(*)::int AS c FROM schema_migrations`);
      expect(applied.rows[0].c).toBe(8);

      // audit_logs فقط‌افزودنی است
      await client.query(
        `INSERT INTO audit_logs (action, entity_type) VALUES ('test.create', 'test')`,
      );
      await expect(client.query(`UPDATE audit_logs SET action = 'test.update'`)).rejects.toThrow();

      const downCount = await migrate.runDown(client, { log: () => undefined });
      expect(downCount).toBe(8);
      const gone = await client.query(`SELECT to_regclass('public.users') AS t`);
      expect(gone.rows[0].t).toBeNull();
    } finally {
      await client.end().catch(() => undefined);
      if (adminConnected) {
        await admin.query(`DROP DATABASE IF EXISTS ${dbName}`).catch(() => undefined);
        await admin.end();
      }
    }
  }, 60000);
});
