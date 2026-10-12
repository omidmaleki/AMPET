import { randomUUID } from 'crypto';
import { NextFunction, Request, Response } from 'express';

/**
 * میدل‌ور تولید/انتقال `X-Request-Id` (UUID) — SP-00 / M-00.4.
 * اگر کلاینت گذرانده، همان منتقل می‌شود (ردیابی یکپارچه در لاگ/پشتیبانی)؛
 * وگرنه UUID جدید ساخته و در هدر پاسخ هم قرار می‌گیرد.
 */
export function requestIdMiddleware(req: Request, res: Response, next: NextFunction): void {
  const incoming = req.headers['x-request-id'];
  const requestId: string =
    typeof incoming === 'string' && incoming.length > 0 && incoming.length <= 64
      ? incoming
      : randomUUID();
  req.headers['x-request-id'] = requestId;
  res.setHeader('X-Request-Id', requestId);
  next();
}
