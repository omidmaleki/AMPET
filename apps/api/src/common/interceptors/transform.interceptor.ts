import { CallHandler, ExecutionContext, Injectable, NestInterceptor } from '@nestjs/common';
import { Observable, map } from 'rxjs';
import { isPaginatedPayload, PaginationMeta } from '../pagination/pagination';

export interface Envelope<T> {
  success: boolean;
  data: T;
  meta: Record<string, unknown> | null;
  error: null;
}

/**
 * اینترسپتور پاسخ موفق — قالب `{success:true,data,meta}` (README قاعده ۵).
 * خروجی‌های صفحه‌بندی‌شده (دارای items + meta) به‌صورت خودکار meta می‌گیرند؛
 * بقیه meta خالی دارند تا ساختار در همه پاسخ‌ها ثابت بماند. (SP-00 / M-00.4)
 */
@Injectable()
export class TransformInterceptor<T> implements NestInterceptor<T, Envelope<T>> {
  intercept(_context: ExecutionContext, next: CallHandler<T>): Observable<Envelope<T>> {
    return next.handle().pipe(
      map((payload) => {
        if (
          payload &&
          typeof payload === 'object' &&
          (payload as unknown as Envelope<T>).success === true
        ) {
          // از قبل envelope — عبور کن (نکته: پروژه فقط همین یک مسیر دارد)
          return payload as unknown as Envelope<T>;
        }
        let data = payload;
        let meta: Record<string, unknown> | null = null;
        if (isPaginatedPayload(payload)) {
          data = payload.items as unknown as T;
          const m: PaginationMeta = payload.meta;
          meta = { page: m.page, per_page: m.per_page, next_cursor: m.next_cursor, total: m.total };
        } else if (payload === undefined) {
          data = null as unknown as T;
        }
        return { success: true, data, meta, error: null };
      }),
    );
  }
}
