/** قرارداد پیامک — امضای interface هم‌ارز کاوه‌نگار (SP-00 / M-00.8؛ واقعی در SP-11). */
export type SmsPurpose = 'OTP' | '2FA';

export interface SmsSendParams {
  phone: string;
  /** کد قالب ۷۸تایی (SP-11) — برای mock هر رشته پذیرفته است */
  templateCode: string;
  params: Record<string, string>;
}

export interface SmsResult {
  messageId: string;
  success: boolean;
}

export interface SmsProvider {
  sendOtp(phone: string, code: string, purpose?: SmsPurpose): Promise<SmsResult>;
  send(params: SmsSendParams): Promise<SmsResult>;
}

export const SMS_PROVIDER = 'SMS_PROVIDER';
