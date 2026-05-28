'use client'

import { Search } from 'lucide-react'
import { usePathname, useRouter, useSearchParams } from 'next/navigation'
import { useEffect, useState } from 'react'
import { Input } from '@/components/ui/input'

export function ProductSearch() {
  const router = useRouter()
  const pathname = usePathname()
  const searchParams = useSearchParams()
  const [value, setValue] = useState(searchParams.get('search') ?? '')

  useEffect(() => {
    const timeout = window.setTimeout(() => {
      const next = new URLSearchParams(searchParams.toString())
      if (value.trim()) {
        next.set('search', value.trim())
      } else {
        next.delete('search')
      }
      next.delete('skip')
      router.replace(`${pathname}?${next.toString()}`)
    }, 300)

    return () => window.clearTimeout(timeout)
  }, [pathname, router, searchParams, value])

  return (
    <div className="relative">
      <Search className="pointer-events-none absolute left-3 top-2.5 h-4 w-4 text-slate-500" />
      <Input value={value} onChange={(event) => setValue(event.target.value)} className="pl-9" />
    </div>
  )
}
