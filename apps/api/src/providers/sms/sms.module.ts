import { Global, Module, Provider } from '@nestjs/common';
import { MockSmsProvider } from './mock-sms.provider';
import { SMS_PROVIDER } from './sms-provider';

const smsProvider: Provider = {
  provide: SMS_PROVIDER,
  useFactory: () => {
    const mode = process.env.SMS_PROVIDER ?? 'mock';
    if (mode === 'kavenegar') {
      // واقعی در SP-11 — اینجا عمداً خطای شفاف می‌دهیم
      throw new Error('SMS_PROVIDER=kavenegar در SP-11 پیاده می‌شود؛ فعلاً mock.');
    }
    return new MockSmsProvider();
  },
};

/** کانال پیامک mock — سراسری (SP-00 / M-00.8) */
@Global()
@Module({
  providers: [smsProvider, MockSmsProvider],
  exports: [SMS_PROVIDER, MockSmsProvider],
})
export class SmsModule {}
