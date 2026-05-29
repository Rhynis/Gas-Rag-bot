'use client'

import { useState } from 'react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { apiClient } from '@/lib/api/client'
import type { KnowledgeBaseDocument, KnowledgeCategory } from '@/components/admin/knowledge-base/kb-form'

interface SearchResult
  extends Pick<KnowledgeBaseDocument, 'id' | 'title' | 'content' | 'category' | 'source'> {
  similarity: number
}

export function KbSearchTest() {
  const [query, setQuery] = useState('')
  const [category, setCategory] = useState<KnowledgeCategory | ''>('')
  const [results, setResults] = useState<SearchResult[]>([])
  const [isSearching, setIsSearching] = useState(false)

  async function handleSearch() {
    if (!query.trim()) return
    setIsSearching(true)
    try {
      const response = await apiClient.post<SearchResult[]>('/api/v1/knowledge-base/search', {
        query,
        top_k: 5,
        category: category || null,
        use_hybrid: true,
      })
      setResults(response.data)
    } catch (caught) {
      toast.error(caught instanceof Error ? caught.message : 'Không thể tìm kiếm')
    } finally {
      setIsSearching(false)
    }
  }

  return (
    <section className="space-y-4 rounded-lg border bg-white p-4">
      <div className="flex flex-wrap items-end gap-3">
        <div className="min-w-64 flex-1">
          <Textarea
            className="min-h-24"
            placeholder="Nhập câu hỏi để kiểm tra truy hồi..."
            value={query}
            onChange={(event) => setQuery(event.target.value)}
          />
        </div>
        <select
          className="h-10 rounded-md border bg-white px-3 text-sm"
          value={category}
          onChange={(event) => setCategory(event.target.value as KnowledgeCategory | '')}
        >
          <option value="">Tất cả</option>
          <option value="safety">An toàn</option>
          <option value="product_info">Sản phẩm</option>
          <option value="delivery">Giao hàng</option>
          <option value="pricing">Giá bán</option>
          <option value="company">Công ty</option>
          <option value="faq">FAQ</option>
          <option value="technical">Kỹ thuật</option>
        </select>
        <Button onClick={() => void handleSearch()} disabled={isSearching}>
          {isSearching ? 'Đang tìm...' : 'Tìm thử'}
        </Button>
      </div>
      {results.length > 0 ? (
        <div className="space-y-3">
          {results.map((result) => (
            <article key={result.id} className="rounded-md border p-3">
              <div className="flex items-center justify-between gap-3">
                <h3 className="font-medium">{result.title}</h3>
                <span className="text-sm text-slate-600">
                  {(result.similarity * 100).toFixed(1)}%
                </span>
              </div>
              <p className="mt-2 line-clamp-3 text-sm text-slate-700">{result.content}</p>
            </article>
          ))}
        </div>
      ) : null}
    </section>
  )
}
