import { existsSync, readFileSync, rmSync } from 'fs';
import * as path from 'path';
import { MockSmsProvider } from '../../src/providers/sms/mock-sms.provider';

/** mock پیامک → لاگ `logs/sms-mock.log` (SP-00 §4 سناریوی دستی ۱۱ / M-00.8) */
describe('Mock SMS provider (SP-00 §4)', () => {
  const logFile = path.resolve(process.cwd(), '..', '..', 'logs', 'sms-mock.log');

  afterAll(() => {
    if (existsSync(logFile)) rmSync(logFile, { force: true });
  });

  it('writes SMS-OTP record with the 5-digit code and does not crash', async () => {
    const provider = new MockSmsProvider();
    const result = await provider.sendOtp('09120000000', '54321');
    expect(result.success).toBe(true);
    expect(result.messageId).toContain('mock-');

    expect(existsSync(logFile)).toBe(true);
    const content = readFileSync(logFile, 'utf8');
    expect(content).toContain('SMS-OTP');
    expect(content).toContain('phone=09120000000');
    expect(content).toContain('code=54321');
  });

  it('supports generic template sends (SMS-2FA shape)', async () => {
    const provider = new MockSmsProvider();
    await provider.send({
      phone: '09120000001',
      templateCode: 'SMS-2FA',
      params: { code: '11111' },
    });
    const content = readFileSync(logFile, 'utf8');
    expect(content).toContain('SMS-2FA');
  });
});
