import { ConfigService } from '@nestjs/config';
import { JwtService } from '@nestjs/jwt';
import { pickPrimaryRole, isKnownRole } from '../../src/modules/auth/auth.roles';
import { TokenService } from '../../src/modules/auth/token.service';

function makeTokenService(): TokenService {
  const jwt = new JwtService({});
  const config = {
    get: (key: string, def?: unknown) => (process.env[key] as string | undefined) ?? def,
  } as unknown as ConfigService;
  return new TokenService(jwt, config);
}

describe('TokenService (SP-01 M-01.3)', () => {
  const tokens = makeTokenService();

  it('access_token_roundtrip_carries_sub_role_sid', async () => {
    const token = await tokens.signAccess({ id: 'u1', role: 'customer', sid: 's1' });
    const claims = await tokens.verifyAccess(token);
    expect(claims).toMatchObject({ sub: 'u1', role: 'customer', sid: 's1' });
  });

  it('admin_jwt_expires_10min_customer_15min', () => {
    expect(tokens.accessTtlSeconds('customer')).toBe(900);
    expect(tokens.accessTtlSeconds('seller')).toBe(900);
    expect(tokens.accessTtlSeconds('admin_super')).toBe(600);
    expect(tokens.accessTtlSeconds('accountant')).toBe(600);
  });

  it('refresh_token_roundtrip_and_unique_per_call', async () => {
    const a = await tokens.signRefresh('s1');
    const b = await tokens.signRefresh('s1');
    expect(a).not.toBe(b); // jti یکتا ⇒ چرخش قابل تشخیص

    const claims = await tokens.verifyRefresh(a);
    expect(claims).toMatchObject({ sid: 's1', type: 'refresh' });
  });

  it('access_token_is_not_valid_as_refresh', async () => {
    const access = await tokens.signAccess({ id: 'u1', role: 'customer', sid: 's1' });
    await expect(tokens.verifyRefresh(access)).rejects.toBeDefined();
  });
});

describe('RBAC role helpers (SP-01 M-01.4)', () => {
  it('pickPrimaryRole chooses highest precedence', () => {
    expect(pickPrimaryRole(['customer'])).toBe('customer');
    expect(pickPrimaryRole(['customer', 'admin_super'])).toBe('admin_super');
    expect(pickPrimaryRole(['seller', 'provider'])).toBe('seller');
    expect(pickPrimaryRole([])).toBe('customer');
  });

  it('isKnownRole rejects courier and unknown', () => {
    expect(isKnownRole('customer')).toBe(true);
    expect(isKnownRole('courier')).toBe(false);
    expect(isKnownRole('ceo')).toBe(false);
  });
});
