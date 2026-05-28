'use client'

import { Search } from 'lucide-react'
import { usePathname, useRouter, useSearchParams } from 'next/navigation'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'

const sizes = ['6', '12', '45']

export function ProductFilters() {
  const router = useRouter()
  const pathname = usePathname()
  const searchParams = useSearchParams()
  const [search, setSearch] = useState(searchParams.get('search') ?? '')
  const [brand, setBrand] = useState(searchParams.get('brand') ?? '')
  const [size, setSize] = useState(searchParams.get('size_kg') ?? 'all')
  const [inStockOnly, setInStockOnly] = useState(searchParams.get('in_stock_only') === 'true')
  const [sort, setSort] = useState(
    `${searchParams.get('sort_by') ?? 'created_at'}:${searchParams.get('sort_order') ?? 'desc'}`
  )

  function applyFilters() {
    const next = new URLSearchParams()
    if (search.trim()) next.set('search', search.trim())
    if (brand.trim()) next.set('brand', brand.trim())
    if (size !== 'all') next.set('size_kg', size)
    if (inStockOnly) next.set('in_stock_only', 'true')
    const [sortBy, sortOrder] = sort.split(':')
    if (sortBy) next.set('sort_by', sortBy)
    if (sortOrder) next.set('sort_order', sortOrder)
    router.replace(`${pathname}?${next.toString()}`)
  }

  function clearFilters() {
    setSearch('')
    setBrand('')
    setSize('all')
    setInStockOnly(false)
    setSort('created_at:desc')
    router.replace(pathname)
  }

  return (
    <div className="rounded-lg border bg-white p-4">
      <div className="grid gap-4 lg:grid-cols-[1.2fr_1fr_160px_180px]">
        <div className="space-y-2">
          <Label htmlFor="search">Tìm kiếm</Label>
          <div className="relative">
            <Search className="pointer-events-none absolute left-3 top-2.5 h-4 w-4 text-slate-500" />
            <Input
              id="search"
              className="pl-9"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === 'Enter') applyFilters()
              }}
            />
          </div>
        </div>
        <div className="space-y-2">
          <Label htmlFor="brand">Thương hiệu</Label>
          <Input id="brand" value={brand} onChange={(event) => setBrand(event.target.value)} />
        </div>
        <div className="space-y-2">
          <Label>Kích thước</Label>
          <Select value={size} onValueChange={setSize}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Tất cả</SelectItem>
              {sizes.map((item) => (
                <SelectItem key={item} value={item}>
                  {item}kg
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div className="space-y-2">
          <Label>Sắp xếp</Label>
          <Select value={sort} onValueChange={setSort}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="created_at:desc">Mới nhất</SelectItem>
              <SelectItem value="price:asc">Giá tăng dần</SelectItem>
              <SelectItem value="price:desc">Giá giảm dần</SelectItem>
              <SelectItem value="name:asc">Tên A-Z</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
      <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
        <label className="flex items-center gap-2 text-sm">
          <Checkbox
            checked={inStockOnly}
            onCheckedChange={(value) => setInStockOnly(value === true)}
          />
          Chỉ hiện sản phẩm còn hàng
        </label>
        <div className="flex gap-2">
          <Button type="button" variant="outline" onClick={clearFilters}>
            Xóa lọc
          </Button>
          <Button type="button" onClick={applyFilters}>
            Áp dụng
          </Button>
        </div>
      </div>
    </div>
  )
}
