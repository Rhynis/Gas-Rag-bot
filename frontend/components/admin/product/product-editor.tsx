'use client'

import { useRouter } from 'next/navigation'
import { toast } from 'sonner'
import { ProductForm } from '@/components/admin/product/product-form'
import { EmptyState } from '@/components/shared/empty-state'
import { PageHeader } from '@/components/shared/page-header'
import { Button } from '@/components/ui/button'
import { useCreateProduct, useProduct, useUpdateProduct } from '@/lib/hooks/use-products'
import type { ProductCreateInput, ProductUpdateInput } from '@/types/product'

type ProductEditorProps = {
  productId?: string
}

export function ProductEditor({ productId }: ProductEditorProps) {
  const router = useRouter()
  const productQuery = useProduct(productId ?? '')
  const createMutation = useCreateProduct()
  const updateMutation = useUpdateProduct()
  const isEditing = Boolean(productId)

  async function handleSubmit(data: ProductCreateInput | ProductUpdateInput) {
    try {
      if (productId) {
        await updateMutation.mutateAsync({ productId, data })
      } else {
        await createMutation.mutateAsync(data as ProductCreateInput)
      }
      router.push('/admin/products')
    } catch (caught) {
      toast.error(caught instanceof Error ? caught.message : 'Không thể lưu sản phẩm')
    }
  }

  if (isEditing && productQuery.isLoading) {
    return (
      <section className="mx-auto max-w-3xl px-4 py-8">
        <PageHeader title="Sửa sản phẩm" />
      </section>
    )
  }

  if (isEditing && !productQuery.data) {
    return (
      <section className="mx-auto max-w-3xl px-4 py-8">
        <EmptyState
          title="Không tìm thấy sản phẩm"
          action={
            <Button variant="outline" onClick={() => router.push('/admin/products')}>
              Quay lại
            </Button>
          }
        />
      </section>
    )
  }

  return (
    <section className="mx-auto max-w-3xl space-y-6 px-4 py-8">
      <PageHeader
        title={isEditing ? 'Sửa sản phẩm' : 'Thêm sản phẩm'}
        description="Quản lý thông tin catalog và tồn kho."
      />
      <div className="rounded-lg border bg-white p-6">
        <ProductForm
          product={productQuery.data}
          isSubmitting={createMutation.isPending || updateMutation.isPending}
          onSubmit={handleSubmit}
        />
      </div>
    </section>
  )
}
