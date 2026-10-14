import type { Metadata } from 'next';
import '../styles/tokens.css';

export const metadata: Metadata = {
  title: 'پنل ادمین AMPET',
  description: 'پنل مدیریت AMPET',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fa" dir="rtl">
      <body>{children}</body>
    </html>
  );
}