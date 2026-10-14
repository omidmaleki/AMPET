import { Injectable, Logger } from '@nestjs/common';
import { RateLimitOptions } from '../decorators/rate-limit.decorator';

export interface RateLimitResult {
  ok: boolean;
  count: number;
  retryAfterMs: number;
}

/**
 * انتزاع نرخ‌گیر — پیاده‌سازی‌ها: حافظه داخلی (پیش‌فرض، بدون وابستگی)
 * و Redis (وقتی REDIS_URL تنظیم شده). (SP-00 / M-00.4 — queue داخلی طبق PLAN §1)
 */
export abstract class RateLimiter {
  abstract increment(key: string, limit: number, windowMs: number): Promise<RateLimitResult>;
}

@Injectable()
export class MemoryRateLimiter extends RateLimiter {
  private readonly store = new Map<string, number[]>();
  private readonly logger = new Logger(MemoryRateLimiter.name);

  async increment(key: string, limit: number, windowMs: number): Promise<RateLimitResult> {
    const now = Date.now();
    const windowStart = now - windowMs;
    const hits = (this.store.get(key) ?? []).filter((ts) => ts > windowStart);
    hits.push(now);
    this.store.set(key, hits);
    // جلوگیری از رشد بی‌نهایت حافظه در dev
    if (this.store.size > 10_000) {
      for (const [k] of this.store) {
        const recent = (this.store.get(k) ?? []).filter((ts) => ts > now - 60_000);
        if (recent.length === 0) this.store.delete(k);
        else this.store.set(k, recent);
      }
    }
    const ok = hits.length <= limit;
    const retryAfterMs = ok ? 0 : Math.max(0, windowMs - (now - hits[0]));
    if (!ok && process.env.NODE_ENV !== 'test') {
      this.logger.warn(`rate limit exceeded key=${key} count=${hits.length}/${limit}`);
    }
    return { ok, count: hits.length, retryAfterMs };
  }

  /** پاک‌سازی در تست‌ها */
  reset(): void {
    this.store.clear();
  }
}

/** تعیین سقف پیش‌فرض از روی مسیر (پروژه‌داک §6). */
export function resolveBucketByPath(path: string): RateLimitOptions {
  const p = `${path}`;
  if (p.includes('/auth/otp/request')) return { limit: 3, windowMs: 10 * 60_000, scope: 'ip+user' };
  if (p.includes('/admin')) return { limit: 120, windowMs: 60_000 };
  if (p.includes('/payments')) return { limit: 10, windowMs: 60_000 };
  return { limit: 60, windowMs: 60_000 };
}

/** کلید نرخ‌گیر بر اساس scope. */
export function buildRateLimitKey(
  req: { ip?: string; user?: { id?: string } },
  path: string,
  options: RateLimitOptions,
): string {
  const scope = options.scope ?? 'ip';
  const ip = (req.ip || 'unknown').replace(/[^0-9a-f.:]/gi, '');
  const userId = (req.user as { id?: string } | undefined)?.id ?? '';
  switch (scope) {
    case 'user':
      return `rl:${path}:user:${userId}`;
    case 'ip+user':
      return `rl:${path}:${ip}:${userId}`;
    case 'ip':
    default:
      return `rl:${path}:${ip}`;
  }
}
