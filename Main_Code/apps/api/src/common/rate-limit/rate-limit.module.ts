import { Global, Module, Provider } from '@nestjs/common';
import Redis from 'ioredis';
import { MemoryRateLimiter, RateLimiter } from './rate-limiter.service';
import { RedisRateLimiter } from './redis-rate-limiter';

export const RATE_LIMITER = 'RATE_LIMITER';

const rateLimiterProvider: Provider = {
  provide: RATE_LIMITER,
  useFactory: (): RateLimiter => {
    const redisUrl = process.env.REDIS_URL;
    if (redisUrl) {
      return new RedisRateLimiter(
        new Redis(redisUrl, { maxRetriesPerRequest: 1, lazyConnect: true }),
      );
    }
    return new MemoryRateLimiter();
  },
};

/** نرخ‌گیر سراسری (SP-00 / M-00.4) — بدون Redis هم کار می‌کند. */
@Global()
@Module({
  providers: [rateLimiterProvider, MemoryRateLimiter],
  exports: [RATE_LIMITER, MemoryRateLimiter],
})
export class RateLimitModule {}
