import { HttpException, HttpStatus } from '@nestjs/common';
import { ErrorCode } from '../error-codes';

/**
 * خطای ساخت‌یافته پروژه — همه خطاهای حوزه کاری از این عبور می‌کنند
 * تا فیلتر سراسری قالب `{success:false,error:{code,message,details,request_id}}`
 * را بدون بازسازی بسازد. (SP-00 / M-00.4)
 */
export class ApiException extends HttpException {
  constructor(
    readonly code: ErrorCode | string,
    status: HttpStatus | number,
    message?: string,
    readonly details: Array<Record<string, unknown>> = [],
  ) {
    super(message ?? code, status);
  }

  static validation(message: string, details: Array<Record<string, unknown>> = []): ApiException {
    return new ApiException(ErrorCode.VALIDATION_ERROR, HttpStatus.BAD_REQUEST, message, details);
  }

  static notFound(message = 'این مورد یافت نشد'): ApiException {
    return new ApiException(ErrorCode.NOT_FOUND, HttpStatus.NOT_FOUND, message);
  }
}
