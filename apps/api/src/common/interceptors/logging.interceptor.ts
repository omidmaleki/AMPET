import { CallHandler, ExecutionContext, Injectable, Logger, NestInterceptor } from '@nestjs/common';
import { Request, Response } from 'express';
import { Observable, tap } from 'rxjs';

/**
 * لاگ ساختاریافته هر درخواست — مسیر، متد، کد وضعیت، زمان پاسخ و `X-Request-Id`
 * و **بدون هیچ PII** (نه بدنه، نه کوئری، نه IP). (SP-00 / M-00.4 گام ۶)
 *
 * ثبت در سطح `Logger` انجام می‌شود؛ در `NODE_ENV=test` لاگرها خاموش‌اند (app.factory).
 */
@Injectable()
export class LoggingInterceptor implements NestInterceptor {
  private readonly logger = new Logger('HTTP');

  intercept(context: ExecutionContext, next: CallHandler): Observable<unknown> {
    const ctx = context.switchToHttp();
    const req = ctx.getRequest<Request>();
    const res = ctx.getResponse<Response>();
    const requestId = (req.headers['x-request-id'] as string | undefined) ?? '';
    const method = req.method;
    const url = req.originalUrl ?? req.url;
    const start = Date.now();

    return next.handle().pipe(
      tap({
        next: () => this.write(method, url, res.statusCode, Date.now() - start, requestId),
        error: (err: unknown) => {
          const status =
            typeof (err as { getStatus?: () => number })?.getStatus === 'function'
              ? (err as { getStatus: () => number }).getStatus()
              : 500;
          this.write(method, url, status, Date.now() - start, requestId);
        },
      }),
    );
  }

  private write(method: string, url: string, status: number, ms: number, requestId: string): void {
    this.logger.log(`request_id=${requestId} ${method} ${url} ${status} ${ms}ms`);
  }
}
