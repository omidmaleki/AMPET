/** انواع مشترک ماژول Auth (SP-01). */

/** کاربر تأییدشده از روی Access JWT — روی `req.user` می‌نشیند. */
export interface AuthUser {
  /** `sub` توکن = users.id */
  id: string;
  /** نقش اصلی (برای RBAC/ماتریس) */
  role: string;
  /** شناسه نشست = sessions.id (`sid`) */
  sid: string;
}

/** claimهای Access JWT (SP-01 M-01.3). */
export interface AccessClaims {
  sub: string;
  role: string;
  sid: string;
  iat?: number;
  exp?: number;
}

/** claimهای Refresh JWT — چرخشی ۳۰ روزه (jti یکتا برای تشخیص استفاده مجدد). */
export interface RefreshClaims {
  sid: string;
  type: 'refresh';
  jti?: string;
  iat?: number;
  exp?: number;
}

/** نتیجه صدور توکن. */
export interface IssuedTokens {
  access_token: string;
  refresh_token: string;
  /** عمر Access بر حسب ثانیه (۹۰۰ مشتری / ۶۰۰ ادمین). */
  expires_in: number;
}
