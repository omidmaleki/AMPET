import { randomUUID } from 'crypto';
import { appendFileSync, mkdirSync } from 'fs';
import * as path from 'path';
import { SmsProvider, SmsResult, SmsSendParams } from './sms-provider';

/** آخرین کد ارسالی (برای تست/مشاهده) — STORAGE دیگر نیست؛ فقط در mock */
const lastCodeByPhone = new Map<string, string>();

/**
 * پیامک mock — لاگ کنسول + فایل `logs/sms-mock.log` با قالب
 * `[ISO] SMS-OTP phone=0912... code=12345` (SP-00 / M-00.8 — PLAN §1).
 * همان امضای interface کاوه‌نگار؛ تعویض با `SMS_PROVIDER=kavenegar` در SP-11.
 */
export class MockSmsProvider implements SmsProvider {
  private readonly logFile: string;

  constructor(logFile?: string) {
    // پیش‌فرض: ریشه ریپو/logs/sms-mock.log (نسبت به apps/api)
    this.logFile = logFile ?? path.resolve(process.cwd(), '..', '..', 'logs', 'sms-mock.log');
  }

  async sendOtp(phone: string, code: string): Promise<SmsResult> {
    lastCodeByPhone.set(phone, code);
    this.write(`SMS-OTP phone=${phone} code=${code}`);
    return { messageId: `mock-${randomUUID()}`, success: true };
  }

  async send(params: SmsSendParams): Promise<SmsResult> {
    this.write(
      `${params.templateCode} phone=${params.phone} params=${JSON.stringify(params.params)}`,
    );
    return { messageId: `mock-${randomUUID()}`, success: true };
  }

  private write(line: string): void {
    const iso = new Date().toISOString();
    const record = `[${iso}] ${line}\n`;
    // eslint-disable-next-line no-console
    console.log(record.trimEnd());
    try {
      mkdirSync(path.dirname(this.logFile), { recursive: true });
      appendFileSync(this.logFile, record, 'utf8');
    } catch {
      /* لاگ نویسی نباید کرش کند */
    }
  }
}

/** دسترسی تست: آخرین کد برای یک شماره */
export function lastOtpForPhone(phone: string): string | undefined {
  return lastCodeByPhone.get(phone);
}
