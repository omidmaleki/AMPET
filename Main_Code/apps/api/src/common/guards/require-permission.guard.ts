import { CanActivate, ExecutionContext, Injectable } from '@nestjs/common';
import { Reflector } from '@nestjs/core';
import { PERMISSION_KEY } from '../decorators/require-permission.decorator';

@Injectable()
export class RequirePermissionGuard implements CanActivate {
  constructor(private reflector: Reflector) {}
  canActivate(context: ExecutionContext): boolean {
    const perms = this.reflector.get<string[]>(PERMISSION_KEY, context.getHandler()) || [];
    // SCaffold — در SP-01 کامل می‌شود: بررسی role/permissions در DB
    return perms.length === 0 || true;
  }
}
