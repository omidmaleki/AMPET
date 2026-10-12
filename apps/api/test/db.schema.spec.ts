import { Client } from 'pg';
// eslint-disable-next-line @typescript-eslint/no-var-requires
const migrate = require('../scripts/migrate.js');

/**
 * قیدهای پایه ERD گروه Auth/User (SP-00 §4):
 *   - db/users_phone_is_unique_and_soft_deletable
 *   - db/audit_logs_rejects_update_and_delete
 *
 * روی یک دیتابیس تازه و مجزا اجرا می‌شود؛ بدون `DATABASE_URL` رد (skip) می‌شود
 * تا توسعهٔ بدون Postgres ممکن بماند. در CI با سرویس Postgres اجرا می‌شود.
 */
const dbUrl = process.env.DATABASE_URL;
const maybe = dbUrl ? describe : describe.skip;

maybe('DB schema constraints — Auth/User (SP-00 §4)', () => {
  let client: Client;
  let admin: Client;
  let adminConnected = false;
  let dbName: string;

  beforeAll(async () => {
    const base = new URL(dbUrl as string);
    dbName = `ampet_db_${Date.now()}`;
    const adminUrl = new URL(base.toString());
    adminUrl.pathname = '/postgres';
    admin = new Client({ connectionString: adminUrl.toString() });
    await admin.connect();
    adminConnected = true;
    await admin.query(`CREATE DATABASE ${dbName}`);

    const testUrl = new URL(base.toString());
    testUrl.pathname = `/${dbName}`;
    client = new Client({ connectionString: testUrl.toString() });
    await client.connect();
    await migrate.runUp(client, { log: () => undefined });
  }, 60000);

  afterAll(async () => {
    await client?.end().catch(() => undefined);
    if (adminConnected) {
      await admin.query(`DROP DATABASE IF EXISTS ${dbName}`).catch(() => undefined);
      await admin.end();
    }
  });

  it('db/users_phone_is_unique_and_soft_deletable', async () => {
    const phone = '09120000009';
    const first = await client.query<{ id: string }>(
      `INSERT INTO users (phone) VALUES ($1) RETURNING id`,
      [phone],
    );

    // شمارهٔ فعال تکراری باید رد شود (index یکتای جزئی روی deleted_at IS NULL)
    await expect(client.query(`INSERT INTO users (phone) VALUES ($1)`, [phone])).rejects.toThrow();

    // پس از soft-delete، همان شماره باید آزاد شود
    await client.query(`UPDATE users SET deleted_at = now() WHERE id = $1`, [first.rows[0].id]);
    await expect(
      client.query(`INSERT INTO users (phone) VALUES ($1)`, [phone]),
    ).resolves.toBeDefined();
  });

  it('db/audit_logs_rejects_update_and_delete', async () => {
    await client.query(
      `INSERT INTO audit_logs (action, entity_type, entity_id) VALUES ('test.create', 'test', '1')`,
    );

    await expect(client.query(`UPDATE audit_logs SET action = 'test.update'`)).rejects.toThrow();
    await expect(client.query(`DELETE FROM audit_logs`)).rejects.toThrow();
  });
});
