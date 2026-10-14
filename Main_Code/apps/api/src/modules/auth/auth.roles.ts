/** نقش‌های شناخته‌شده و انتخاب نقش اصلی (RBAC — SP-01 M-01.4). */

/** ۸ نقش سیستمی؛ «پیک» عمداً نیست (project-document.md:1334). */
export const KNOWN_ROLES = [
  'customer',
  'seller',
  'provider',
  'admin_super',
  'support',
  'accountant',
  'finance',
  'health_content_manager',
] as const;

export type KnownRole = (typeof KNOWN_ROLES)[number];

/** ترتیب اعتبار نقش‌ها برای انتخاب نقش اصلی JWT (بالاترین اول). */
const ROLE_PRECEDENCE = [
  'admin_super',
  'support',
  'finance',
  'accountant',
  'health_content_manager',
  'seller',
  'provider',
  'customer',
];

/** بالاترین نقش کاربر؛ پیش‌فرض «مشتری». */
export function pickPrimaryRole(roles: string[]): string {
  for (const role of ROLE_PRECEDENCE) {
    if (roles.includes(role)) return role;
  }
  return roles[0] ?? 'customer';
}

export function isKnownRole(role: string): role is KnownRole {
  return (KNOWN_ROLES as readonly string[]).includes(role);
}
