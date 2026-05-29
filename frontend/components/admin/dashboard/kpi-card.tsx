import type { ReactNode } from 'react'

type KpiCardProps = {
  title: string
  value: string
  description?: string
  icon: ReactNode
}

export function KpiCard({ title, value, description, icon }: KpiCardProps) {
  return (
    <article className="rounded-lg border bg-white p-4 shadow-sm">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="text-sm font-medium text-slate-600">{title}</p>
          <p className="mt-2 text-2xl font-semibold text-slate-950">{value}</p>
          {description ? <p className="mt-1 text-sm text-slate-500">{description}</p> : null}
        </div>
        <div className="flex h-10 w-10 items-center justify-center rounded-md bg-slate-100 text-slate-700">
          {icon}
        </div>
      </div>
    </article>
  )
}
