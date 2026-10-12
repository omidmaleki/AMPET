import { INestApplication } from '@nestjs/common';
import request = require('supertest');
import { createApp } from '../src/app.factory';

/**
 * rate_limit/public_61st_request_in_minute_returns_429_with_retry_after (SP-00 §4)
 * (هر فایل نمونه اپ مستقل دارد ⇒ نرخ‌گیر حافظه‌ای تازه)
 */
describe('Rate limit — public bucket (SP-00 §4)', () => {
  let app: INestApplication;

  beforeAll(async () => {
    app = await createApp();
    await app.init();
  });

  afterAll(async () => {
    await app.close();
  });

  it('public_61st_request_in_minute_returns_429_with_retry_after', async () => {
    let last: request.Response | undefined;
    let firstStatus = 0;
    for (let i = 1; i <= 61; i += 1) {
      const res = await request(app.getHttpServer()).get('/api/v1/health');
      if (i === 1) firstStatus = res.status;
      last = res;
    }
    expect(firstStatus).toBe(200);
    expect(last!.status).toBe(429);
    expect(last!.body.success).toBe(false);
    expect(last!.body.error.code).toBe('RATE_LIMIT_EXCEEDED');
    expect(last!.headers['retry-after']).toBeDefined();
    expect(Number(last!.headers['retry-after'])).toBeGreaterThan(0);
    expect(last!.headers['x-ratelimit-limit']).toBe('60');
  });
});
