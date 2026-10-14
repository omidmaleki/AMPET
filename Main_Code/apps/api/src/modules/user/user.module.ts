import { Module } from '@nestjs/common';
import { SessionController } from './session.controller';

/** ماژول User — بدون کد فیچر در SP-00. پروفایل/نشست/حذف حساب → SP-01، آدرس/حیوان → SP-02. */
@Module({
  controllers: [SessionController],
})
export class UserModule {}

