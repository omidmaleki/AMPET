/** قرارداد درگاه پرداخت — mock فعلاً؛ زرین‌پال Sandbox در SP-07. (SP-00 / M-00.8) */
export interface PaymentInitRequest {
  orderRef: string;
  amount: number; // تومان
  description?: string;
  callbackUrl: string;
  meta?: Record<string, unknown>;
}

export interface PaymentInitResult {
  authority: string;
  redirectUrl: string;
}

export interface PaymentVerifyResult {
  status: 'paid' | 'failed' | 'pending';
  orderRef: string;
  amount: number;
  referenceId: string;
}

export interface PaymentGateway {
  createPayment(req: PaymentInitRequest): Promise<PaymentInitResult>;
  verify(authority: string): Promise<PaymentVerifyResult>;
}

export const PAYMENT_GATEWAY = 'PAYMENT_GATEWAY';
