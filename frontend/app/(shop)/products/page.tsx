import { PageHeader } from '@/components/shared/page-header'
import { ProductFilters } from '@/components/shop/product-filters'
import { ProductGrid } from '@/components/shop/product-grid'
import { ProductPagination } from '@/components/shop/product-pagination'
import type { ProductListResponse, ProductSearchParams } from '@/types/product'

type ProductsPageProps = {
  searchParams: Promise<Record<string, string | string[] | undefined>>
}

const emptyProductList: ProductListResponse = {
  items: [],
  total: 0,
  page: 1,
  limit: 20,
  has_more: false,
}

function firstValue(value: string | string[] | undefined): string | undefined {
  return Array.isArray(value) ? value[0] : value
}

function parseProductParams(
  params: Record<string, string | string[] | undefined>
): ProductSearchParams {
  const sortBy = firstValue(params.sort_by)
  const sortOrder = firstValue(params.sort_order)

  return {
    search: firstValue(params.search),
    brand: firstValue(params.brand),
    min_price: firstValue(params.min_price),
    max_price: firstValue(params.max_price),
    size_kg: firstValue(params.size_kg),
    in_stock_only: firstValue(params.in_stock_only) === 'true',
    sort_by: sortBy === 'price' || sortBy === 'name' ? sortBy : 'created_at',
    sort_order: sortOrder === 'asc' ? 'asc' : 'desc',
    skip: Number.parseInt(firstValue(params.skip) ?? '0', 10),
    limit: Number.parseInt(firstValue(params.limit) ?? '20', 10),
  }
}

async function getInitialProducts(params: ProductSearchParams): Promise<ProductListResponse> {
  const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'
  const url = new URL('/api/v1/products', apiBaseUrl)
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== '' && value !== false) {
      url.searchParams.set(key, String(value))
    }
  })

  try {
    const response = await fetch(url, { cache: 'no-store' })
    if (!response.ok) return emptyProductList
    return (await response.json()) as ProductListResponse
  } catch {
    return emptyProductList
  }
}

export default async function ProductsPage({ searchParams }: ProductsPageProps) {
  const resolvedSearchParams = await searchParams
  const params = parseProductParams(resolvedSearchParams)
  const products = await getInitialProducts(params)

  return (
    <section className="mx-auto max-w-6xl space-y-6 px-4 py-8">
      <PageHeader
        title="Sản phẩm gas LPG"
        description="Chọn bình gas phù hợp cho gia đình hoặc nhu cầu kinh doanh."
      />
      <ProductFilters />
      <div className="flex items-center justify-between text-sm text-slate-600">
        <span>{products.total.toLocaleString('vi-VN')} sản phẩm</span>
        <span>Trang {products.page.toLocaleString('vi-VN')}</span>
      </div>
      <ProductGrid products={products.items} />
      <ProductPagination page={products.page} limit={products.limit} hasMore={products.has_more} />
    </section>
  )
}
