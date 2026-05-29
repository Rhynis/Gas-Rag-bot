import type { Metadata } from 'next'
import { Toaster } from 'sonner'
import { Providers } from '@/components/providers'
import { Header } from '@/components/shared/header'
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
            <Header />
            <main>{children}</main>
          </div>
          <Toaster richColors position="top-right" />
        </Providers>
      </body>
    </html>
  )
}
