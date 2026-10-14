export default function HomePage() {
  return (
    <main style={{ padding: 24 }}>
      <h1 style={{ color: 'var(--ampet-primary)' }}>پنل ادمین AMPET</h1>
      <p style={{ color: 'var(--ampet-text-secondary)' }}>
        اسکافولد SP-00 — صفحات ادمین (۱۴ و ۱۳) در SP-03 و ۴۸ صفحه کامل در SP-15 ساخته می‌شوند.
      </p>
      <p>
        مستندات API (Swagger):{' '}
        <a href="http://localhost:3000/docs">http://localhost:3000/docs</a>
      </p>
    </main>
  );
}