import { Module } from '@nestjs/common';
import { AuthModule } from '../auth/auth.module';
import { AdminController } from './admin.controller';

/** ماژول ادمین SP-01 (M-01.4): لیست کاربران + تغییر نقش + تأیید 2FA. صفحات وب → SP-15. */
@Module({
  imports: [AuthModule],
  controllers: [AdminController],
})
export class AdminModule {}
