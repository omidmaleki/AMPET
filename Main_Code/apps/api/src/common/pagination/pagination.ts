/** ساختار صفحه‌بندی استاندارد (project-document §5). */
export interface PaginationMeta {
  page: number;
  per_page: number;
  next_cursor: string | null;
  total: number;
}

export interface Paginated<T> {
  items: T[];
  meta: PaginationMeta;
}

/** نشان‌دهنده خروجی صفحه‌بندی‌شده (اینترسپتور آن را به meta تبدیل می‌کند). */
export function isPaginatedPayload(value: unknown): value is Paginated<unknown> {
  return (
    !!value &&
    typeof value === 'object' &&
    Array.isArray((value as Paginated<unknown>).items) &&
    !!((value as Paginated<unknown>).meta as unknown as Record<string, unknown> | undefined)?.page
  );
}
