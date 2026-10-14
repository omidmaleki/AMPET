import { Module, ValidationPipe } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import { APP_FILTER, APP_GUARD, APP_INTERCEPTOR, APP_PIPE } from '@nestjs/core';
import * as path from 'path';
import { validateEnv } from './config/env.validation';
import { DatabaseModule } from './database/database.module';
import { AllExceptionsFilter } from './common/filters/all-exceptions.filter';
import { RateLimitGuard } from './common/guards/rate-limit.guard';
import { LoggingInterceptor } from './common/interceptors/logging.interceptor';
import { TransformInterceptor } from './common/interceptors/transform.interceptor';
import { RateLimitModule } from './common/rate-limit/rate-limit.module';
import { AdminModule } from './modules/admin/admin.module';
import { AuthModule } from './modules/auth/auth.module';
import { HealthModule } from './modules/health/health.module';
import { MarketplaceModule } from './modules/marketplace/marketplace.module';
import { PaymentModule } from './modules/payment/payment.module';
import { SandboxModule } from './modules/sandbox/sandbox.module';
import { UserModule } from './modules/user/user.module';
import { PaymentGatewayModule } from './providers/payment/payment-gateway.module';
import { SmsModule } from './providers/sms/sms.module';

/**
 * ریشه اپ — مونولیت ماژولار (D-001). لایه قراردادی سراسری (envelope/خطا/نرخ‌گیر/
 * اعتبارسنجی) این‌جا به‌صورت APP_* ثبت شده تا در تست هم بدون بازسازی فعال باشد.
 */
@Module({
  imports: [
    ConfigModule.forRoot({
      isGlobal: true,
      envFilePath: [path.resolve(process.cwd(), '..', '..', '.env'), '.env'],
      validate: validateEnv,
    }),
    RateLimitModule,
    DatabaseModule,
    SmsModule,
    PaymentGatewayModule,
    // ماژول‌های دامنه (بدون کد فیچر در SP-00)
    AuthModule,
    UserModule,
    MarketplaceModule,
    PaymentModule,
    AdminModule,
    // ماژول‌های عملیاتی SP-00
    HealthModule,
    SandboxModule,
  ],
  providers: [
    { provide: APP_GUARD, useClass: RateLimitGuard },
    { provide: APP_INTERCEPTOR, useClass: TransformInterceptor },
    { provide: APP_INTERCEPTOR, useClass: LoggingInterceptor },
    { provide: APP_FILTER, useClass: AllExceptionsFilter },
    {
      provide: APP_PIPE,
      useValue: new ValidationPipe({
        whitelist: true,
        forbidNonWhitelisted: true,
        transform: true,
        transformOptions: { enableImplicitConversion: true },
      }),
    },
  ],
})
export class AppModule {}
