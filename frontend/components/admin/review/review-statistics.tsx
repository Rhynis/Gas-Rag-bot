'use client'

import { BarChart3, CheckCircle2, Clock, Database, XCircle } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import type { ReviewStatistics as ReviewStatisticsType } from '@/lib/api/review'

type ReviewStatisticsProps = {
  statistics?: ReviewStatisticsType
}

export function ReviewStatistics({ statistics }: ReviewStatisticsProps) {
  const total = statistics?.total_flagged ?? 0
  const approvedRate = total ? Math.round(((statistics?.approved ?? 0) / total) * 100) : 0
  const byIntent = Object.entries(statistics?.by_intent ?? {})

  return (
    <div className="space-y-4">
      <div className="grid gap-3 md:grid-cols-4">
        <MetricCard icon={Clock} label="Đang chờ" value={statistics?.pending ?? 0} />
        <MetricCard icon={CheckCircle2} label="% phê duyệt" value={`${approvedRate}%`} />
        <MetricCard icon={Database} label="Đã thêm KB" value={statistics?.added_to_kb ?? 0} />
        <MetricCard icon={XCircle} label="Từ chối" value={statistics?.rejected ?? 0} />
      </div>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <BarChart3 className="h-4 w-4" />
            Theo intent
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          {byIntent.length ? (
            byIntent.map(([intent, count]) => (
              <div key={intent} className="space-y-1">
                <div className="flex justify-between text-sm">
                  <span>{intent}</span>
                  <span>{count}</span>
                </div>
                <div className="h-2 rounded-full bg-slate-100">
                  <div
                    className="h-2 rounded-full bg-slate-900"
                    style={{ width: `${Math.max(8, (count / Math.max(total, 1)) * 100)}%` }}
                  />
                </div>
              </div>
            ))
          ) : (
            <p className="text-sm text-slate-500">Chưa có dữ liệu review.</p>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

function MetricCard({
  icon: Icon,
  label,
  value,
}: {
  icon: typeof Clock
  label: string
  value: string | number
}) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center gap-2 text-sm font-medium text-slate-600">
          <Icon className="h-4 w-4" />
          {label}
        </CardTitle>
      </CardHeader>
      <CardContent className="text-2xl font-semibold">{value}</CardContent>
    </Card>
  )
}
