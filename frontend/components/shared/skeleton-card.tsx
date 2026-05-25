export function SkeletonCard() {
  return (
    <div className="animate-pulse rounded-lg border p-4">
      <div className="h-36 rounded-md bg-slate-200" />
      <div className="mt-4 h-4 w-2/3 rounded bg-slate-200" />
      <div className="mt-2 h-4 w-1/2 rounded bg-slate-200" />
    </div>
  )
}
