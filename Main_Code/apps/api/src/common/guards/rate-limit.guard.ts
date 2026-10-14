import {
  CanActivate,
  ExecutionContext,
  HttpStatus,
  Inject,
  Injectable,
  Logger,
} from '@nestjs/common';
import { Reflector } from '@nestjs/core';
import { Request, Response } from 'express';
import { RATE_LIMIT_METADATA, RateLimitOptions } from '../decorators/rate-limit.decorator';
import { ErrorCode } from '../error-codes';
import { ApiException } from '../exceptions/api.exception';
import {
  buildRateLimitKey,
  RateLimiter,
  resolveBucketByPath,
} from '../rate-limit/rate-limiter.service';
import { RATE_LIMITER } from '../rate-limit/rate-limit.module';

/**
 * گارد سراسری نرخ — سقف‌ها: عمومی ۶۰/دقیقه، پایه‌رداخت ۱۰/دقیقه، ادمین ۱۲۰/دقیقه،
 * OTP ۳/۱۰دقیقه. پاسخ 429 + هدر Retry-After. (SP-00 / M-00.4)
 */
@Injectable()
export class RateLimitGuard implements CanActivate {
  private readonly logger = new Logger(RateLimitGuard.name);

  constructor(
    @Inject(RATE_LIMITER) private readonly limiter: RateLimiter,
    private readonly reflector: Reflector,
  ) {}

  async canActivate(context: ExecutionContext): Promise<boolean> {
    const request = context.switchToHttp().getRequest<Request>();
    const response = context.switchToHttp().getResponse<Response>();
    const path: string = request.route?.path ?? request.originalUrl ?? request.url;

    const declared = this.reflector.getAllAndOverride<RateLimitOptions | undefined>(
      RATE_LIMIT_METADATA,
      [context.getHandler(), context.getClass()],
    );
    const options: RateLimitOptions = declared ?? resolveBucketByPath(path);

    const key = buildRateLimitKey(request, path, options);
    const result = await this.limiter.increment(key, options.limit, options.windowMs);

    response.setHeader('X-RateLimit-Limit', String(options.limit));
    if (!result.ok) {
      const retryAfterSeconds = Math.max(1, Math.ceil(result.retryAfterMs / 1000));
      response.setHeader('Retry-After', String(retryAfterSeconds));
      response.setHeader('X-RateLimit-Remaining', '0');
      throw new ApiException(
        ErrorCode.RATE_LIMIT_EXCEEDED,
        HttpStatus.TOO_MANY_REQUESTS,
        'تعداد درخواست‌ها بیش از حد مجاز است؛ کمی بعد دوباره تلاش کنید',
        [{ retry_after_seconds: retryAfterSeconds }],
      );
    }
    response.setHeader('X-RateLimit-Remaining', String(options.limit - result.count));
    return true;
  }
}
