'use client'

import Link from 'next/link'
import { ShoppingBag } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { CartReviewStep } from '@/components/shop/checkout/cart-review-step'
import { OrderSummarySidebar } from '@/components/shop/checkout/order-summary-sidebar'
import { PageHeader } from '@/components/shared/page-header'

export default function CartPage() {
  return (
    <section className="mx-auto max-w-6xl space-y-6 px-4 py-8">
      <PageHeader title="Giỏ hàng" description="Kiểm tra sản phẩm trước khi thanh toán." />
      <div className="grid gap-6 lg:grid-cols-[1fr_320px]">
        <CartReviewStep
          onNext={() => {
            window.location.href = '/checkout'
          }}
        />
        <OrderSummarySidebar />
      </div>
      <Button asChild variant="outline">
        <Link href="/products">
          <ShoppingBag className="mr-2 h-4 w-4" />
          Tiếp tục mua hàng
        </Link>
      </Button>
    </section>
  )
}
