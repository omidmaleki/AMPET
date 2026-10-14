import { Module } from '@nestjs/common';
import { AuthModule } from '../auth/auth.module';
import { SessionController } from './session.controller';

/** ماژول User — پروفایل/نشست/حذف حساب (SP-01)، آدرس/حیوان → SP-02. */
@Module({
  imports: [AuthModule],
  controllers: [SessionController],
})
export class UserModule {}
