import type { Metadata } from 'next'
import Link from 'next/link'
import { Toaster } from 'sonner'
import { Providers } from '@/components/providers'
import './globals.css'

export const metadata: Metadata = {
  title: 'GasBot Vietnam',
  description: 'Mua gas LPG online với AI hỗ trợ 24/7',
  openGraph: {
    title: 'GasBot Vietnam',
    description: 'Mua gas LPG online với AI hỗ trợ 24/7',
    locale: 'vi_VN',
    type: 'website',
  },
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="vi">
      <body>
        <Providers>
          <div className="min-h-screen bg-slate-50">
            <header className="border-b bg-white">
              <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4">
                <Link href="/" className="text-lg font-semibold text-orange-700">
                  GasBot Vietnam
                </Link>
                <nav className="flex items-center gap-4 text-sm">
                  <Link href="/products">Sản phẩm</Link>
                  <Link href="/cart">Giỏ hàng</Link>
                  <Link href="/login">Đăng nhập</Link>
                </nav>
              </div>
            </header>
            <main>{children}</main>
          </div>
          <Toaster richColors position="top-right" />
        </Providers>
      </body>
    </html>
  )
}
