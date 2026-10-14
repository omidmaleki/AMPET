import { Module } from '@nestjs/common';
import { ConfigModule, ConfigService } from '@nestjs/config';
import { JwtModule } from '@nestjs/jwt';
import { AuthController } from './auth.controller';
import { AuthService } from './auth.service';
import { JwtAuthGuard } from './jwt-auth.guard';
import { OtpService } from './otp.service';
import { AuditRepository } from './repositories/audit.repository';
import { OtpRepository } from './repositories/otp.repository';
import { SessionRepository } from './repositories/session.repository';
import { UserRepository } from './repositories/user.repository';
import { SessionService } from './session.service';
import { TokenService } from './token.service';
import { RequirePermissionGuard } from '../../common/guards/require-permission.guard';

/**
 * ماژول Auth + User + RBAC (SP-01). لایه دیتابیس سراسری است (DatabaseModule).
 * `JwtModule` با راز Access ثبت می‌شود؛ راز Refresh جداگانه در TokenService امضا می‌شود.
 */
@Module({
  imports: [
    JwtModule.registerAsync({
      imports: [ConfigModule],
      inject: [ConfigService],
      useFactory: (cfg: ConfigService) => ({
        secret: cfg.get<string>('JWT_ACCESS_SECRET', 'change_me_access_32chars_min'),
        signOptions: { expiresIn: '15m' },
      }),
    }),
  ],
  controllers: [AuthController],
  providers: [
    TokenService,
    OtpService,
    SessionService,
    AuthService,
    UserRepository,
    OtpRepository,
    SessionRepository,
    AuditRepository,
    JwtAuthGuard,
    RequirePermissionGuard,
  ],
  exports: [
    TokenService,
    AuthService,
    SessionService,
    UserRepository,
    OtpRepository,
    SessionRepository,
    AuditRepository,
    JwtAuthGuard,
    RequirePermissionGuard,
  ],
})
export class AuthModule {}
