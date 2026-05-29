'use client'

import {
  CircleDollarSign,
  Clock3,
  PackageSearch,
  ShoppingCart,
  UserPlus,
  Users,
} from 'lucide-react'
import { KpiCard } from '@/components/admin/dashboard/kpi-card'
import { useAdminDashboard } from '@/lib/hooks/use-admin'
import { formatNumber, formatPrice } from '@/lib/utils/format'

export function StatsOverview() {
  const { data, isLoading } = useAdminDashboard()

  if (isLoading) {
    return (
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {Array.from({ length: 6 }).map((_, index) => (
          <div key={index} className="h-32 rounded-lg border bg-white p-4 shadow-sm">
            <div className="h-4 w-24 rounded bg-slate-200" />
            <div className="mt-5 h-7 w-20 rounded bg-slate-200" />
            <div className="mt-3 h-4 w-32 rounded bg-slate-100" />
          </div>
        ))}
      </div>
    )
  }

  const stats = data ?? {
    orders_today: 0,
    orders_pending: 0,
    revenue_today: 0,
    low_stock_count: 0,
    users_total: 0,
    users_new_today: 0,
  }

  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
      <KpiCard
        title="Đơn hôm nay"
        value={formatNumber(stats.orders_today)}
        description="Đơn được tạo trong ngày"
        icon={<ShoppingCart className="h-5 w-5" />}
      />
      <KpiCard
        title="Đơn chờ xử lý"
        value={formatNumber(stats.orders_pending)}
        description="Cần xác nhận hoặc điều phối"
        icon={<Clock3 className="h-5 w-5" />}
      />
      <KpiCard
        title="Doanh thu hôm nay"
        value={formatPrice(stats.revenue_today)}
        description="Không tính đơn đã hủy"
        icon={<CircleDollarSign className="h-5 w-5" />}
      />
      <KpiCard
        title="Tồn kho thấp"
        value={formatNumber(stats.low_stock_count)}
        description="Sản phẩm cần kiểm tra"
        icon={<PackageSearch className="h-5 w-5" />}
      />
      <KpiCard
        title="Người dùng"
        value={formatNumber(stats.users_total)}
        description="Tổng tài khoản trong hệ thống"
        icon={<Users className="h-5 w-5" />}
      />
      <KpiCard
        title="Người dùng mới"
        value={formatNumber(stats.users_new_today)}
        description="Tài khoản tạo hôm nay"
        icon={<UserPlus className="h-5 w-5" />}
      />
    </div>
  )
}
