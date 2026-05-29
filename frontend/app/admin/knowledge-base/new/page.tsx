import { KbForm } from '@/components/admin/knowledge-base/kb-form'
import { PageHeader } from '@/components/shared/page-header'

export default function NewKnowledgeBasePage() {
  return (
    <section className="space-y-6">
      <PageHeader title="Thêm tài liệu KB" description="Tạo tài liệu mới và sinh embedding." />
      <KbForm />
    </section>
  )
}
