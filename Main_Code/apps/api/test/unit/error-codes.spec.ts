import { DEFAULT_CODE_BY_STATUS, ErrorCode, MESSAGE_BY_CODE } from '../../src/common/error-codes';

/** انطباق کاتالوگ کدها با docs/error-codes.md (SP-00 §4) */
describe('Error code catalog (SP-00 §4)', () => {
  it('every error code has a non-empty Persian message', () => {
    for (const code of Object.values(ErrorCode)) {
      const message = MESSAGE_BY_CODE[code as ErrorCode];
      expect(typeof message).toBe('string');
      expect((message ?? '').length).toBeGreaterThan(0);
      expect(message).toMatch(/[\u0600-\u06FF]/);
    }
  });

  it('contains fields for every StatusCode in the base document §4', () => {
    const statuses = [400, 401, 403, 404, 409, 422, 429, 500, 502, 503];
    for (const status of statuses) {
      expect(DEFAULT_CODE_BY_STATUS[status]).toBeDefined();
    }
    expect(DEFAULT_CODE_BY_STATUS[400]).toBe(ErrorCode.VALIDATION_ERROR);
    expect(DEFAULT_CODE_BY_STATUS[404]).toBe(ErrorCode.NOT_FOUND);
    expect(DEFAULT_CODE_BY_STATUS[429]).toBe(ErrorCode.RATE_LIMIT_EXCEEDED);
  });

  it('contains the decision codes added by sub-projects', () => {
    expect(ErrorCode.PRICE_OUT_OF_BAND).toBe('PRICE_OUT_OF_BAND');
    expect(ErrorCode.DELIVERY_CODE_INVALID).toBe('DELIVERY_CODE_INVALID');
    expect(ErrorCode.TICKET_LIMIT_REACHED).toBe('TICKET_LIMIT_REACHED');
  });
});
