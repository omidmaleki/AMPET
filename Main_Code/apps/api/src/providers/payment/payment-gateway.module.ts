import { Global, Module, Provider } from '@nestjs/common';
import { MockPaymentGateway } from './mock-payment.gateway';
import { PAYMENT_GATEWAY } from './payment-gateway';

const paymentProvider: Provider = {
  provide: PAYMENT_GATEWAY,
  useFactory: () => {
    const mode = process.env.PAYMENT_GATEWAY ?? 'mock';
    if (mode === 'zarinpal') {
      // واقعی در SP-07
      throw new Error('PAYMENT_GATEWAY=zarinpal در SP-07 پیاده می‌شود؛ فعلاً mock.');
    }
    return new MockPaymentGateway();
  },
};

/** درگاه پرداخت mock — سراسری (SP-00 / M-00.8) */
@Global()
@Module({
  providers: [paymentProvider, MockPaymentGateway],
  exports: [PAYMENT_GATEWAY, MockPaymentGateway],
})
export class PaymentGatewayModule {}
