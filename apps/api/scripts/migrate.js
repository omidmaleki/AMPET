#!/usr/bin/env node
/**
 * اجراکننده مهاجرت AMPET (SP-00 / M-00.6) — بدون وابستگی به ORM.
 * - up:   اعمال فایل‌های src/migrations/up/*.sql به ترتیب نسخه (idempotent)
 * - down: برگشت به ترتیب معکوس با فایل‌های src/migrations/down/<version>.sql
 * ثبت وضعیت در جدول schema_migrations. هر فایل در یک تراکنش.
 *
 * استفاده:
 *   node scripts/migrate.js up
 *   node scripts/migrate.js down
 */
'use strict';

const fs = require('fs');
const path = require('path');
const { Client } = require('pg');

const upDir = path.join(__dirname, '..', 'src', 'migrations', 'up');
const downDir = path.join(__dirname, '..', 'src', 'migrations', 'down');

function defaultUrl() {
  return (
    process.env.DATABASE_URL ||
    'postgresql://ampet:ampet_dev_password_change_me@localhost:5432/ampet_dev'
  );
}

function listSql(dir) {
  if (!fs.existsSync(dir)) return [];
  return fs
    .readdirSync(dir)
    .filter((f) => f.endsWith('.sql'))
    .sort();
}

async function ensureTable(client) {
  await client.query(`CREATE TABLE IF NOT EXISTS schema_migrations (
    version    varchar(120) PRIMARY KEY,
    name       varchar(160) NOT NULL,
    applied_at timestamptz  NOT NULL DEFAULT now()
  )`);
}

async function appliedVersions(client) {
  const { rows } = await client.query('SELECT version FROM schema_migrations');
  return new Set(rows.map((r) => r.version));
}

async function runUp(client, logger = console) {
  await ensureTable(client);
  const applied = await appliedVersions(client);
  let count = 0;
  for (const file of listSql(upDir)) {
    const version = file.replace(/\.sql$/, '');
    if (applied.has(version)) continue;
    const sql = fs.readFileSync(path.join(upDir, file), 'utf8');
    await client.query('BEGIN');
    try {
      await client.query(sql);
      await client.query('INSERT INTO schema_migrations (version, name) VALUES ($1, $2)', [
        version,
        file,
      ]);
      await client.query('COMMIT');
      count += 1;
      logger.log(`  up   ${file}`);
    } catch (e) {
      await client.query('ROLLBACK');
      throw new Error(`مهاجرت ${file} شکست خورد: ${e.message}`);
    }
  }
  logger.log(`up کامل شد — ${count} مهاجرت اعمال شد.`);
  return count;
}

async function runDown(client, logger = console) {
  await ensureTable(client);
  const { rows } = await client.query(
    'SELECT version, name FROM schema_migrations ORDER BY version DESC',
  );
  let count = 0;
  for (const row of rows) {
    const downFile = path.join(downDir, `${row.version}.sql`);
    await client.query('BEGIN');
    try {
      if (fs.existsSync(downFile)) {
        await client.query(fs.readFileSync(downFile, 'utf8'));
        logger.log(`  down ${row.name}`);
      } else {
        logger.log(`  down ${row.name} (placeholder — بدون عملیات)`);
      }
      await client.query('DELETE FROM schema_migrations WHERE version = $1', [row.version]);
      await client.query('COMMIT');
      count += 1;
    } catch (e) {
      await client.query('ROLLBACK');
      throw new Error(`rollback ${row.name} شکست خورد: ${e.message}`);
    }
  }
  logger.log(`down کامل شد — ${count} مهاجرت برگشت.`);
  return count;
}

async function main() {
  const mode = (process.argv[2] || 'up').toLowerCase();
  const client = new Client({ connectionString: defaultUrl() });
  await client.connect();
  try {
    if (mode === 'down') await runDown(client);
    else await runUp(client);
  } finally {
    await client.end();
  }
}

if (require.main === module) {
  main().catch((e) => {
    console.error(e.message || e);
    process.exit(1);
  });
}

module.exports = { runUp, runDown, ensureTable, defaultUrl, upDir, downDir };