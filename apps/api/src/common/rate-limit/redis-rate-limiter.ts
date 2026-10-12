import Redis from 'ioredis';
import { RateLimiter, RateLimitResult } from './rate-limiter.service';

/**
 * پیاده‌سازی Redis (شمارنده atomic) — وقتی REDIS_URL موجود باشد استفاده می‌شود.
 * CI و prod از همین استفاده می‌کنند؛ dev بدون Redis به حافظه داخلی برمی‌گردد.
 */
export class RedisRateLimiter extends RateLimiter {
  constructor(private readonly redis: Redis) {
    super();
  }

  async increment(key: string, limit: number, windowMs: number): Promise<RateLimitResult> {
    const script = `
      local c = redis.call('INCR', KEYS[1])
      if c == 1 then redis.call('PEXPIRE', KEYS[1], ARGV[1]) end
      return c
    `;
    const count = (await this.redis.eval(script, 1, key, String(windowMs))) as number;
    let retryAfterMs = 0;
    if (count > limit) {
      const ttl = await this.redis.pttl(key);
      retryAfterMs = ttl > 0 ? ttl : 0;
    }
    return { ok: count <= limit, count, retryAfterMs };
  }
}
