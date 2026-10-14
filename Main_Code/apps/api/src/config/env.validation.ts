/**
 * اعتبارسنجی سبک متغیرهای محیطی (بدون وابستگی Joi).
 * عمداً حداقل است تا dev/تست بدون سکرت هم بالا بیاید؛ سکرت واقعی prod در SP-16 سخت‌گیر می‌شود.
 */
export function validateEnv(config: Record<string, unknown>): Record<string, unknown> {
  const errors: string[] = [];

  if (config.PORT !== undefined && Number.isNaN(Number(config.PORT))) {
    errors.push('PORT باید عدد باشد');
  }
  const nodeEnv = String(config.NODE_ENV ?? 'development');
  if (!['development', 'test', 'production'].includes(nodeEnv)) {
    errors.push(`NODE_ENV نامعتبر است: ${nodeEnv}`);
  }
  const smsProvider = String(config.SMS_PROVIDER ?? 'mock');
  if (!['mock', 'kavenegar'].includes(smsProvider)) {
    errors.push(`SMS_PROVIDER نامعتبر است: ${smsProvider}`);
  }
  const payGateway = String(config.PAYMENT_GATEWAY ?? 'mock');
  if (!['mock', 'zarinpal'].includes(payGateway)) {
    errors.push(`PAYMENT_GATEWAY نامعتبر است: ${payGateway}`);
  }

  if (errors.length > 0) {
    throw new Error(`خطای پیکربندی محیط (.env):\n - ${errors.join('\n - ')}`);
  }
  return config;
}
