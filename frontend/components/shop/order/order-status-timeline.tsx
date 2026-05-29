'use client'

import { CheckCircle2, Circle } from 'lucide-react'
import { cn } from '@/lib/utils'
import type { OrderStatus } from '@/types/order'

const steps: Array<{ status: OrderStatus; label: string }> = [
  { status: 'pending', label: 'Chờ xác nhận' },
  { status: 'confirmed', label: 'Đã xác nhận' },
  { status: 'shipping', label: 'Đang giao' },
  { status: 'delivered', label: 'Đã giao' },
]

export function OrderStatusTimeline({ status }: { status: OrderStatus }) {
  if (status === 'cancelled') {
    return (
      <p className="rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700">
        Đơn hàng đã hủy
      </p>
    )
  }
  const currentIndex = steps.findIndex((step) => step.status === status)
  return (
    <div className="grid gap-3 sm:grid-cols-4">
      {steps.map((step, index) => {
        const complete = index <= currentIndex
        return (
          <div key={step.status} className="flex items-center gap-2">
            {complete ? (
              <CheckCircle2 className="h-5 w-5 text-emerald-600" />
            ) : (
              <Circle className="h-5 w-5 text-slate-300" />
            )}
            <span className={cn('text-sm', complete ? 'font-medium' : 'text-slate-500')}>
              {step.label}
            </span>
          </div>
        )
      })}
    </div>
  )
}
