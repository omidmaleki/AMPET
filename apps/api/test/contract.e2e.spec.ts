import { INestApplication } from '@nestjs/common';
import request = require('supertest');
import { createApp } from '../src/app.factory';

/**
 * تست‌های قراردادی سراسری SP-00 (§۴):
 *  - contract/envelope_success_has_success_data_meta
 *  - contract/error_shape_has_code_fa_message_details_request_id
 *  - contract/unknown_route_returns_404_NOT_FOUND
 *  - contract/validation_error_returns_400_with_fa_message
 */
describe('Global API contract (SP-00 §4)', () => {
  let app: INestApplication;

  beforeAll(async () => {
    app = await createApp();
    await app.init();
  });

  afterAll(async () => {
    await app.close();
  });

  it('envelope_success_has_success_data_meta', async () => {
    const res = await request(app.getHttpServer()).get('/api/v1/health').expect(200);
    expect(res.body.success).toBe(true);
    expect(res.body).toHaveProperty('data');
    expect(res.body).toHaveProperty('meta');
    expect(res.body.error).toBeNull();
    expect(res.headers['x-request-id']).toBeDefined();
  });

  it('envelope carries pagination meta for paginated payloads', async () => {
    const res = await request(app.getHttpServer()).get('/api/v1/sandbox/paginated').expect(200);
    expect(res.body.success).toBe(true);
    expect(Array.isArray(res.body.data)).toBe(true);
    expect(res.body.meta).toMatchObject({ page: 1, per_page: 20, total: 3 });
  });

  it('unknown_route_returns_404_NOT_FOUND', async () => {
    const res = await request(app.getHttpServer()).get('/api/v1/definitely-not-here').expect(404);
    expect(res.body.success).toBe(false);
    expect(res.body.error.code).toBe('NOT_FOUND');
  });

  it('error_shape_has_code_fa_message_details_request_id', async () => {
    const res = await request(app.getHttpServer()).get('/api/v1/sandbox/error-demo').expect(422);
    expect(res.body.success).toBe(false);
    expect(res.body.data).toBeNull();
    expect(res.body.error.code).toBe('STOCK_UNAVAILABLE');
    // پیام فارسی (نه انگلیسی)
    expect(res.body.error.message).toMatch(/[\u0600-\u06FF]/);
    expect(Array.isArray(res.body.error.details)).toBe(true);
    expect(typeof res.body.error.request_id).toBe('string');
    expect(res.body.error.request_id.length).toBeGreaterThan(0);
    expect(res.headers['x-request-id']).toBe(res.body.error.request_id);
  });

  it('validation_error_returns_400_with_fa_message', async () => {
    const res = await request(app.getHttpServer())
      .post('/api/v1/sandbox/echo')
      .send({})
      .expect(400);
    expect(res.body.success).toBe(false);
    expect(res.body.error.code).toBe('VALIDATION_ERROR');
    expect(res.body.error.message).toMatch(/[\u0600-\u06FF]/);
    expect(Array.isArray(res.body.error.details)).toBe(true);
    expect(res.body.error.details.length).toBeGreaterThan(0);
    expect(res.body.error.request_id).toBeDefined();
  });

  it('valid body echoes back inside the envelope', async () => {
    const res = await request(app.getHttpServer())
      .post('/api/v1/sandbox/echo')
      .send({ name: 'آمپت' })
      .expect(201);
    expect(res.body.success).toBe(true);
    expect(res.body.data).toEqual({ name: 'آمپت' });
  });
});
