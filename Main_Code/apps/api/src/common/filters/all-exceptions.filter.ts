import {
  ArgumentsHost,
  Catch,
  ExceptionFilter,
  HttpException,
  HttpStatus,
  Logger,
} from '@nestjs/common';
import { Request, Response } from 'express';
import { DEFAULT_CODE_BY_STATUS, ErrorCode, MESSAGE_BY_CODE } from '../error-codes';
import { ApiException } from '../exceptions/api.exception';

interface ErrorBody {
  code: string;
  message: string;
  details: Array<Record<string, unknown>>;
  request_id: string;
}

export interface ErrorEnvelope {
  success: boolean;
  data: null;
  error: ErrorBody;
}

/**
 * فیلتر سراسری خطا — همه خطاها را به قالب
 * `{success:false, data:null, error:{code,message,details,request_id}}` تبدیل می‌کند
 * با `message` فارسی و `request_id` از هدر. (SP-00 / M-00.4)
 */
@Catch()
export class AllExceptionsFilter implements ExceptionFilter {
  private readonly logger = new Logger(AllExceptionsFilter.name);

  catch(exception: unknown, host: ArgumentsHost): void {
    const ctx = host.switchToHttp();
    const res = ctx.getResponse<Response>();
    const req = ctx.getRequest<Request>();
    const requestId = (req.headers['x-request-id'] as string | undefined) ?? '';

    let status = HttpStatus.INTERNAL_SERVER_ERROR;
    let code: string = ErrorCode.INTERNAL_ERROR;
    let message: string = MESSAGE_BY_CODE[ErrorCode.INTERNAL_ERROR];
    let details: Array<Record<string, unknown>> = [];

    if (exception instanceof ApiException) {
      status = exception.getStatus();
      code = exception.code;
      message =
        typeof exception.getResponse() === 'string'
          ? (exception.getResponse() as string)
          : exception.message;
      details = exception.details;
    } else if (exception instanceof HttpException) {
      status = exception.getStatus();
      const body = exception.getResponse();
      if (typeof body === 'string') {
        message = body;
      } else if (body && typeof body === 'object') {
        const obj = body as Record<string, unknown>;
        if (typeof obj.message === 'string') message = obj.message;
        else if (Array.isArray(obj.message)) {
          // پیام‌های class-validator: به‌صورت آرایه می‌آیند
          message = 'درخواست نامعتبر است؛ فیلدها را بررسی کنید';
          details = (obj.message as string[]).slice(0, 10).map((m) => ({ message: m }));
        }
        if (typeof obj.code === 'string') code = obj.code;
      }
      if (code === ErrorCode.INTERNAL_ERROR) {
        code = DEFAULT_CODE_BY_STATUS[status] ?? ErrorCode.INTERNAL_ERROR;
      }
      if (message === (exception.getResponse() as unknown) || message === code) {
        message = MESSAGE_BY_CODE[code as ErrorCode] ?? 'خطایی رخ داد';
      }
    } else {
      // خطای ناخواسته — لاگ با request_id (بدون PII) و پاسخ عمومی 500
      this.logger.error(
        `request_id=${requestId} path=${req.method} ${req.originalUrl} unhandled=${String(exception)}`,
      );
    }

    res.status(status);
    if (requestId) res.setHeader('X-Request-Id', requestId);
    // اگر جزئیات شامل retry_after_seconds باشد، هدر استاندارد Retry-After ست شود
    const retryAfter = details.find((d) => typeof d.retry_after_seconds === 'number');
    if (retryAfter) res.setHeader('Retry-After', String(retryAfter.retry_after_seconds));
    const envelope: ErrorEnvelope = {
      success: false,
      data: null,
      error: { code, message, details, request_id: requestId },
    };
    res.json(envelope);
  }
}
