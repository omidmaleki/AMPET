import { Request } from 'express';
import { RequestContext } from './auth.service';

/** استخراج زمینه نشست از هدرهای HTTP (SP-01 M-01.3). */
export function toRequestContext(
  req: Request,
  overrides?: { device_id?: string; platform?: string },
): RequestContext {
  const h = req.headers;
  return {
    ip: req.ip ?? null,
    userAgent: typeof h['user-agent'] === 'string' ? h['user-agent'] : null,
    deviceId:
      overrides?.device_id ?? (typeof h['x-device-id'] === 'string' ? h['x-device-id'] : null),
    platform: overrides?.platform ?? (typeof h['x-platform'] === 'string' ? h['x-platform'] : null),
    requestId: typeof h['x-request-id'] === 'string' ? h['x-request-id'] : null,
  };
}
