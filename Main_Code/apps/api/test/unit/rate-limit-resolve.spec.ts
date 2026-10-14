import { resolveBucketByPath } from '../../src/common/rate-limit/rate-limiter.service';

/** rate_limit/admin_bucket_is_120_per_minute_and_payment_is_10 (SP-00 §4) */
describe('Rate limit bucket resolution (SP-00 §4)', () => {
  it('rate_limit/admin_bucket_is_120_per_minute_and_payment_is_10', () => {
    expect(resolveBucketByPath('/api/v1/admin/master-products')).toMatchObject({
      limit: 120,
      windowMs: 60_000,
    });
    expect(resolveBucketByPath('/api/v1/payments')).toMatchObject({
      limit: 10,
      windowMs: 60_000,
    });
  });

  it('public routes default to 60 per minute', () => {
    expect(resolveBucketByPath('/api/v1/health')).toMatchObject({ limit: 60, windowMs: 60_000 });
    expect(resolveBucketByPath('/api/v1/products')).toMatchObject({ limit: 60 });
  });

  it('otp request is 3 per 10 minutes', () => {
    expect(resolveBucketByPath('/api/v1/auth/otp/request')).toMatchObject({
      limit: 3,
      windowMs: 600_000,
    });
  });
});
