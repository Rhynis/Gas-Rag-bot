'use client'

import { useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { apiClient } from '@/lib/api/client'

export type KnowledgeCategory =
  | 'safety'
  | 'product_info'
  | 'delivery'
  | 'pricing'
  | 'company'
  | 'faq'
  | 'technical'

export interface KnowledgeBaseDocument {
  id: string
  title: string
  content: string
  category: KnowledgeCategory
  source: string | null
  metadata: Record<string, unknown>
  is_active: boolean
  created_at: string
  updated_at: string
}

type KbFormProps = {
  documentId?: string
}

const categoryOptions: Array<{ value: KnowledgeCategory; label: string }> = [
  { value: 'safety', label: 'An toàn' },
  { value: 'product_info', label: 'Sản phẩm' },
  { value: 'delivery', label: 'Giao hàng' },
  { value: 'pricing', label: 'Giá bán' },
  { value: 'company', label: 'Công ty' },
  { value: 'faq', label: 'FAQ' },
  { value: 'technical', label: 'Kỹ thuật' },
]

export function KbForm({ documentId }: KbFormProps) {
  const router = useRouter()
  const [title, setTitle] = useState('')
  const [content, setContent] = useState('')
  const [category, setCategory] = useState<KnowledgeCategory>('faq')
  const [source, setSource] = useState('')
  const [isLoading, setIsLoading] = useState(Boolean(documentId))
  const [isSaving, setIsSaving] = useState(false)

  useEffect(() => {
    if (!documentId) return
    let mounted = true
    async function loadDocument() {
      setIsLoading(true)
      try {
        const response = await apiClient.get<KnowledgeBaseDocument>(
          `/api/v1/admin/knowledge-base/${documentId}`
        )
        if (!mounted) return
        setTitle(response.data.title)
        setContent(response.data.content)
        setCategory(response.data.category)
        setSource(response.data.source ?? '')
      } catch (caught) {
        toast.error(caught instanceof Error ? caught.message : 'Không thể tải tài liệu')
      } finally {
        if (mounted) setIsLoading(false)
      }
    }
    void loadDocument()
    return () => {
      mounted = false
    }
  }, [documentId])

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setIsSaving(true)
    try {
      const payload = {
        title,
        content,
        category,
        source: source || null,
        metadata: {},
      }
      if (documentId) {
        await apiClient.patch(`/api/v1/admin/knowledge-base/${documentId}`, payload)
        toast.success('Đã cập nhật tài liệu')
      } else {
        await apiClient.post('/api/v1/admin/knowledge-base', payload)
        toast.success('Đã tạo tài liệu')
      }
      router.push('/admin/knowledge-base')
    } catch (caught) {
      toast.error(caught instanceof Error ? caught.message : 'Không thể lưu tài liệu')
    } finally {
      setIsSaving(false)
    }
  }

  if (isLoading) {
    return <div className="rounded-lg border bg-white p-6 text-sm text-slate-600">Đang tải...</div>
  }

  return (
    <form className="space-y-5 rounded-lg border bg-white p-5" onSubmit={handleSubmit}>
      <div className="space-y-2">
        <Label htmlFor="kb-title">Tiêu đề</Label>
        <Input
          id="kb-title"
          value={title}
          onChange={(event) => setTitle(event.target.value)}
          required
        />
      </div>
      <div className="grid gap-4 sm:grid-cols-2">
        <div className="space-y-2">
          <Label htmlFor="kb-category">Danh mục</Label>
          <select
            id="kb-category"
            className="h-10 w-full rounded-md border bg-white px-3 text-sm"
            value={category}
            onChange={(event) => setCategory(event.target.value as KnowledgeCategory)}
          >
            {categoryOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
        <div className="space-y-2">
          <Label htmlFor="kb-source">Nguồn</Label>
          <Input
            id="kb-source"
            value={source}
            onChange={(event) => setSource(event.target.value)}
            placeholder="internal_docs"
          />
        </div>
      </div>
      <div className="space-y-2">
        <Label htmlFor="kb-content">Nội dung</Label>
        <Textarea
          id="kb-content"
          className="min-h-80"
          value={content}
          onChange={(event) => setContent(event.target.value)}
          required
        />
      </div>
      <div className="flex justify-end gap-3">
        <Button
          type="button"
          variant="outline"
          onClick={() => router.push('/admin/knowledge-base')}
        >
          Hủy
        </Button>
        <Button type="submit" disabled={isSaving}>
          {isSaving ? 'Đang lưu...' : 'Lưu'}
        </Button>
      </div>
    </form>
  )
}

export { categoryOptions }
