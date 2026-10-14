import { CanActivate, ExecutionContext, HttpStatus, Injectable } from '@nestjs/common';
import { Reflector } from '@nestjs/core';
import { ErrorCode } from '../error-codes';
import { ApiException } from '../exceptions/api.exception';
import { PERMISSION_KEY } from '../decorators/require-permission.decorator';
import { AuditRepository } from '../../modules/auth/repositories/audit.repository';
import { UserRepository } from '../../modules/auth/repositories/user.repository';
import { AuthUser } from '../../modules/auth/auth.types';

interface RequestWithUser {
  user?: AuthUser;
  ip?: string;
  headers: Record<string, unknown>;
}

/**
 * گارد RBAC سراسری (SP-01 M-01.4):
 * - متادیتای `@RequirePermission` را می‌خواند؛ بدون متادیتا عبور می‌کند
 * - مجوزهای مؤثر کاربر را از نقش‌هایش می‌سنجد
 * - تلاش ممنوع در `audit_logs` ثبت می‌شود (قاعده «لاگ اقدامات»)
 */
@Injectable()
export class RequirePermissionGuard implements CanActivate {
  constructor(
    private readonly reflector: Reflector,
    private readonly users: UserRepository,
    private readonly audit: AuditRepository,
  ) {}

  async canActivate(context: ExecutionContext): Promise<boolean> {
    const required =
      this.reflector.getAllAndOverride<string[]>(PERMISSION_KEY, [
        context.getHandler(),
        context.getClass(),
      ]) ?? [];
    if (required.length === 0) return true;

    const req = context.switchToHttp().getRequest<RequestWithUser>();
    const user = req.user;
    if (!user) {
      throw new ApiException(
        ErrorCode.TOKEN_EXPIRED,
        HttpStatus.UNAUTHORIZED,
        'نشست شما پایان یافت؛ برای امنیت بیشتر دوباره وارد شوید',
      );
    }

    const granted = await this.users.permissions(user.id);
    const ok = required.every((p) => granted.includes(p));
    if (!ok) {
      await this.audit.record({
        actorId: user.id,
        action: 'rbac.permission_denied',
        entityType: 'permission',
        entityId: required.join(','),
        after: { required, granted },
        ip: req.ip ?? null,
        requestId:
          typeof req.headers['x-request-id'] === 'string'
            ? (req.headers['x-request-id'] as string)
            : null,
      });
      throw new ApiException(ErrorCode.FORBIDDEN_ROLE, HttpStatus.FORBIDDEN, 'سطح دسترسی ناکافی');
    }
    return true;
  }
}
