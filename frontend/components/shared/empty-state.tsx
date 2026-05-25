import type { ReactNode } from 'react'

type EmptyStateProps = {
  title: string
  description?: string
  action?: ReactNode
}

export function EmptyState({ title, description, action }: EmptyStateProps) {
  return (
    <div className="flex min-h-48 flex-col items-center justify-center gap-3 rounded-lg border border-dashed p-8 text-center">
      <h2 className="text-lg font-medium">{title}</h2>
      {description ? <p className="max-w-md text-sm text-slate-600">{description}</p> : null}
      {action}
    </div>
  )
}
