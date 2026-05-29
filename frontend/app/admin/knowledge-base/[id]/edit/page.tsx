import { KbForm } from '@/components/admin/knowledge-base/kb-form'
import { PageHeader } from '@/components/shared/page-header'

type EditKnowledgeBasePageProps = {
  params: Promise<{ id: string }>
}

export default async function EditKnowledgeBasePage({ params }: EditKnowledgeBasePageProps) {
  const { id } = await params
  return (
    <section className="space-y-6">
      <PageHeader title="Sửa tài liệu KB" description="Cập nhật nội dung và embedding khi cần." />
      <KbForm documentId={id} />
    </section>
  )
}
