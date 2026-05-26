import { EmptyState } from '@/components/shared/empty-state'
import { ProductCard } from '@/components/shop/product-card'
import type { Product } from '@/types/product'

type ProductGridProps = {
  products: Product[]
}

export function ProductGrid({ products }: ProductGridProps) {
  if (products.length === 0) {
    return (
      <EmptyState
        title="Chưa có sản phẩm phù hợp"
        description="Thử đổi bộ lọc hoặc quay lại sau khi cửa hàng cập nhật tồn kho."
      />
    )
  }

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {products.map((product) => (
        <ProductCard key={product.id} product={product} />
      ))}
    </div>
  )
}
