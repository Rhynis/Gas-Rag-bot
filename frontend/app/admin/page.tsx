'use client'

import { StatsOverview } from '@/components/admin/dashboard/stats-overview'
import { LowStockAlert } from '@/components/admin/product/low-stock-alert'
import { PageHeader } from '@/components/shared/page-header'
import { useAdminDashboard } from '@/lib/hooks/use-admin'

export default function AdminDashboardPage() {
  const { data } = useAdminDashboard()

  return (
    <section className="space-y-6">
      <PageHeader title="Dashboard" description="Tổng quan vận hành bán gas LPG." />
      <LowStockAlert count={data?.low_stock_count ?? 0} />
      <StatsOverview />
    </section>
  )
}
