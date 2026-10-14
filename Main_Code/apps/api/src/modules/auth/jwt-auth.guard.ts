import { CanActivate, ExecutionContext, HttpStatus, Injectable } from '@nestjs/common';
import { Request } from 'express';
import { ErrorCode } from '../../common/error-codes';
import { ApiException } from '../../common/exceptions/api.exception';
import { AuthUser } from './auth.types';
import { TokenService } from './token.service';

export interface AuthedRequest extends Request {
  user?: AuthUser;
}

/**
 * گارد احراز هویت — هدر `Authorization: Bearer <access>`,
 * claims را روی `req.user` می‌نشاند (SP-01 M-01.3).
 */
@Injectable()
export class JwtAuthGuard implements CanActivate {
  constructor(private readonly tokens: TokenService) {}

  async canActivate(context: ExecutionContext): Promise<boolean> {
    const req = context.switchToHttp().getRequest<AuthedRequest>();
    const header = req.headers['authorization'];
    if (!header || !header.startsWith('Bearer ')) {
      throw new ApiException(
        ErrorCode.TOKEN_EXPIRED,
        HttpStatus.UNAUTHORIZED,
        'نشست شما پایان یافت؛ برای امنیت بیشتر دوباره وارد شوید',
      );
    }
    try {
      const claims = await this.tokens.verifyAccess(header.slice(7));
      req.user = { id: claims.sub, role: claims.role, sid: claims.sid };
      return true;
    } catch {
      throw new ApiException(
        ErrorCode.TOKEN_EXPIRED,
        HttpStatus.UNAUTHORIZED,
        'نشست شما پایان یافت؛ برای امنیت بیشتر دوباره وارد شوید',
      );
    }
  }
}
