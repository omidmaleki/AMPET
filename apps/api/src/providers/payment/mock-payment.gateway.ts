import { randomUUID } from 'crypto';
import {
  PaymentGateway,
  PaymentInitRequest,
  PaymentInitResult,
  PaymentVerifyResult,
} from './payment-gateway';

/**
 * درگاه mock — برای SP-00/SP-06/SP-07 تا اتصال زرین‌پال.
 * IDها با پیشوند MOCK- مشخص‌اند تا در لاگ/دیتا از واقعی قابل تفکیک باشند.
 */
export class MockPaymentGateway implements PaymentGateway {
  private readonly authorityByOrder = new Map<string, string>();

  async createPayment(req: PaymentInitRequest): Promise<PaymentInitResult> {
    const authority = `MOCK-${randomUUID()}`;
    this.authorityByOrder.set(authority, req.orderRef);
    return {
      authority,
      redirectUrl: `${req.callbackUrl}?Authority=${authority}&Status=OK`,
    };
  }

  async verify(authority: string): Promise<PaymentVerifyResult> {
    const orderRef = this.authorityByOrder.get(authority) ?? 'unknown';
    return {
      status: 'paid',
      orderRef,
      amount: 0,
      referenceId: `MOCK-REF-${randomUUID()}`,
    };
  }
}
