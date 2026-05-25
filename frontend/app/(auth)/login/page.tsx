import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Đăng nhập | GasBot Vietnam',
}

export default function LoginPage() {
  return (
    <div className="space-y-2">
      <h1 className="text-2xl font-semibold">Đăng nhập</h1>
      <p className="text-sm text-slate-600">Form đăng nhập sẽ được hoàn thiện ở Phase 2.1.</p>
    </div>
  )
}
