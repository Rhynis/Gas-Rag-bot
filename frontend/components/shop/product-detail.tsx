'use client'

import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { toast } from 'sonner'
import { ArrowLeft, Flame, ShieldCheck } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { StockBadge } from '@/components/shop/stock-badge'
import { useCartStore } from '@/lib/stores/cart-store'
import { formatPrice } from '@/lib/utils/format'
import type { Product } from '@/types/product'

type ProductDetailProps = {
  product: Product
}

export function ProductDetail({ product }: ProductDetailProps) {
  const router = useRouter()
  const addItem = useCartStore((state) => state.addItem)
  const inStock = product.stock_quantity > 0
  const addToCart = () => {
    addItem(product, 1)
    toast.success('Đã thêm vào giỏ hàng')
  }

  return (
    <section className="mx-auto max-w-6xl space-y-6 px-4 py-8">
      <Button asChild variant="outline">
        <Link href="/products">
          <ArrowLeft className="mr-2 h-4 w-4" />
          Sản phẩm
        </Link>
      </Button>

      <div className="grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
        <div className="flex aspect-square items-center justify-center rounded-lg border bg-white">
          {product.image_url ? (
            <div
              aria-label={product.name}
              className="h-full w-full rounded-lg bg-cover bg-center"
              style={{ backgroundImage: `url(${product.image_url})` }}
            />
          ) : (
            <Flame className="h-20 w-20 text-primary" />
          )}
        </div>

        <div className="space-y-5">
          <div className="space-y-3">
            <div className="flex flex-wrap gap-2">
              <StockBadge stockQuantity={product.stock_quantity} />
              <Badge variant="outline">{product.brand}</Badge>
              <Badge variant="outline">{Number(product.size_kg).toLocaleString('vi-VN')}kg</Badge>
            </div>
            <h1 className="text-3xl font-semibold tracking-normal text-slate-950 md:text-4xl">
              {product.name}
            </h1>
            <p className="text-3xl font-semibold text-primary">{formatPrice(product.price)}</p>
            <p className="text-sm text-slate-600">SKU {product.sku}</p>
          </div>

          {product.description ? (
            <Card>
              <CardHeader>
                <CardTitle>Mô tả</CardTitle>
              </CardHeader>
              <CardContent className="text-slate-700">{product.description}</CardContent>
            </Card>
          ) : null}

          {product.safety_info ? (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <ShieldCheck className="h-5 w-5 text-primary" />
                  An toàn sử dụng
                </CardTitle>
              </CardHeader>
              <CardContent className="text-slate-700">{product.safety_info}</CardContent>
            </Card>
          ) : null}

          <div className="flex flex-wrap gap-3">
            <Button disabled={!inStock} onClick={addToCart}>
              Thêm vào giỏ
            </Button>
            <Button
              disabled={!inStock}
              variant="outline"
              onClick={() => {
                addItem(product, 1)
                router.push('/checkout')
              }}
            >
              Mua ngay
            </Button>
          </div>
        </div>
      </div>
    </section>
  )
}
