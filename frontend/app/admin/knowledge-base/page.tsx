'use client'

import { FilePlus, Upload } from 'lucide-react'
import Link from 'next/link'
import { useEffect, useState } from 'react'
import { toast } from 'sonner'
import { KbImportDialog } from '@/components/admin/knowledge-base/kb-import-dialog'
import { KbSearchTest } from '@/components/admin/knowledge-base/kb-search-test'
import {
  categoryOptions,
  type KnowledgeBaseDocument,
  type KnowledgeCategory,
} from '@/components/admin/knowledge-base/kb-form'
import { EmptyState } from '@/components/shared/empty-state'
import { PageHeader } from '@/components/shared/page-header'
import { Button } from '@/components/ui/button'
import { apiClient } from '@/lib/api/client'
import { formatDate } from '@/lib/utils/format'

interface KnowledgeBaseListResponse {
  items: KnowledgeBaseDocument[]
  total: number
  page: number
  limit: number
  has_more: boolean
}

export default function AdminKnowledgeBasePage() {
  const [documents, setDocuments] = useState<KnowledgeBaseDocument[]>([])
  const [category, setCategory] = useState<KnowledgeCategory | ''>('')
  const [activeOnly, setActiveOnly] = useState(true)
  const [isLoading, setIsLoading] = useState(true)
  const [importOpen, setImportOpen] = useState(false)
  const [refreshKey, setRefreshKey] = useState(0)

  useEffect(() => {
    let cancelled = false

    async function load() {
      setIsLoading(true)
      try {
        const response = await apiClient.get<KnowledgeBaseListResponse>(
          '/api/v1/admin/knowledge-base',
          { params: { limit: 100, category: category || undefined, active_only: activeOnly } }
        )
        if (!cancelled) setDocuments(response.data.items)
      } catch (caught) {
        if (!cancelled)
          toast.error(caught instanceof Error ? caught.message : 'Không thể tải tài liệu')
      } finally {
        if (!cancelled) setIsLoading(false)
      }
    }

    void load()
    return () => {
      cancelled = true
    }
  }, [activeOnly, category, refreshKey])

  async function deleteDocument(documentId: string) {
    if (!window.confirm('Ẩn tài liệu này khỏi tìm kiếm?')) return
    try {
      await apiClient.delete(`/api/v1/admin/knowledge-base/${documentId}`)
      toast.success('Đã ẩn tài liệu')
      setRefreshKey((k) => k + 1)
    } catch (caught) {
      toast.error(caught instanceof Error ? caught.message : 'Không thể ẩn tài liệu')
    }
  }

  return (
    <section className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <PageHeader
          title="Knowledge Base"
          description="Quản lý tài liệu tiếng Việt dùng cho truy hồi RAG."
        />
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => setImportOpen(true)}>
            <Upload className="h-4 w-4" />
            Nhập
          </Button>
          <Button asChild>
            <Link href="/admin/knowledge-base/new">
              <FilePlus className="h-4 w-4" />
              Thêm
            </Link>
          </Button>
        </div>
      </div>

      <div className="flex flex-wrap gap-3 rounded-lg border bg-white p-4">
        <select
          className="h-10 rounded-md border bg-white px-3 text-sm"
          value={category}
          onChange={(event) => setCategory(event.target.value as KnowledgeCategory | '')}
        >
          <option value="">Tất cả danh mục</option>
          {categoryOptions.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
        <label className="flex items-center gap-2 text-sm text-slate-700">
          <input
            type="checkbox"
            checked={activeOnly}
            onChange={(event) => setActiveOnly(event.target.checked)}
          />
          Chỉ tài liệu đang bật
        </label>
      </div>

      <div className="overflow-x-auto rounded-lg border bg-white">
        <table className="w-full min-w-[820px] text-sm">
          <thead className="bg-slate-100 text-left">
            <tr>
              <th className="p-3">Tiêu đề</th>
              <th className="p-3">Danh mục</th>
              <th className="p-3">Nguồn</th>
              <th className="p-3">Cập nhật</th>
              <th className="p-3 text-right">Thao tác</th>
            </tr>
          </thead>
          <tbody>
            {isLoading ? (
              <tr>
                <td className="p-3 text-slate-600" colSpan={5}>
                  Đang tải...
                </td>
              </tr>
            ) : null}
            {documents.map((document) => (
              <tr key={document.id} className="border-t">
                <td className="p-3">
                  <div className="font-medium">{document.title}</div>
                  <div className="line-clamp-2 text-slate-600">{document.content}</div>
                </td>
                <td className="p-3">{document.category}</td>
                <td className="p-3">{document.source ?? 'Nội bộ'}</td>
                <td className="p-3">{formatDate(document.updated_at, false)}</td>
                <td className="p-3 text-right">
                  <div className="flex justify-end gap-2">
                    <Button asChild variant="outline" size="sm">
                      <Link href={`/admin/knowledge-base/${document.id}/edit`}>Sửa</Link>
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => void deleteDocument(document.id)}
                    >
                      Ẩn
                    </Button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {!isLoading && documents.length === 0 ? (
          <div className="p-6">
            <EmptyState title="Chưa có tài liệu" description="Thêm hoặc nhập tài liệu KB." />
          </div>
        ) : null}
      </div>

      <KbSearchTest />
      <KbImportDialog
        open={importOpen}
        onOpenChange={setImportOpen}
        onImported={() => setRefreshKey((k) => k + 1)}
      />
    </section>
  )
}
