import { ProductEditor } from '@/components/admin/product/product-editor'

type EditProductPageProps = {
  params: Promise<{ id: string }>
}

export default async function EditProductPage({ params }: EditProductPageProps) {
  const { id } = await params
  return <ProductEditor productId={id} />
}
