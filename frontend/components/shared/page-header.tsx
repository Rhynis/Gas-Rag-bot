type PageHeaderProps = {
  title: string
  description?: string
}

export function PageHeader({ title, description }: PageHeaderProps) {
  return (
    <header className="space-y-2">
      <h1 className="text-3xl font-semibold tracking-normal">{title}</h1>
      {description ? <p className="text-slate-600">{description}</p> : null}
    </header>
  )
}
