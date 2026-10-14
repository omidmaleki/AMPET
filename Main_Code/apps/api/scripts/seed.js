#!/usr/bin/env node
/**
 * اجراکننده seed AMPET (SP-01 / M-01.1) — بدون وابستگی به ORM.
 * - فایل‌های src/migrations/seed/*.sql را به ترتیب نام اجرا می‌کند.
 * - اگر ADMIN_PHONE در محیط (‏.env) باشد، به‌عنوان تنظیم جلسه ست می‌شود تا
 *   seed کاربر ادمین اولیه را بسازد (بدون هاردکد شماره در SQL).
 *
 * استفاده:
 *   node scripts/seed.js
 */
'use strict';

const fs = require('fs');
const path = require('path');
const { Client } = require('pg');

const seedDir = path.join(__dirname, '..', 'src', 'migrations', 'seed');

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

async function main() {
  const client = new Client({ connectionString: defaultUrl() });
  await client.connect();
  try {
    if (process.env.ADMIN_PHONE) {
      await client.query(`SELECT set_config('ampet.admin_phone', $1, false)`, [
        process.env.ADMIN_PHONE,
      ]);
    }
    const files = listSql(seedDir);
    for (const file of files) {
      const sql = fs.readFileSync(path.join(seedDir, file), 'utf8');
      await client.query('BEGIN');
      try {
        await client.query(sql);
        await client.query('COMMIT');
        console.log(`  seed ${file}`);
      } catch (e) {
        await client.query('ROLLBACK');
        throw new Error(`seed ${file} شکست خورد: ${e.message}`);
      }
    }
    console.log(`seed کامل شد — ${files.length} فایل.`);
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

module.exports = { main, listSql, defaultUrl, seedDir };
