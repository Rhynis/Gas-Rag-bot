'use client'

import { useState } from 'react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { apiClient } from '@/lib/api/client'
import { categoryOptions, type KnowledgeCategory } from '@/components/admin/knowledge-base/kb-form'

type KbImportDialogProps = {
  open: boolean
  onOpenChange: (open: boolean) => void
  onImported: () => void
}

export function KbImportDialog({ open, onOpenChange, onImported }: KbImportDialogProps) {
  const [file, setFile] = useState<File | null>(null)
  const [category, setCategory] = useState<KnowledgeCategory | ''>('')
  const [isImporting, setIsImporting] = useState(false)

  async function handleImport() {
    if (!file) return
    const formData = new FormData()
    formData.append('file', file)
    setIsImporting(true)
    try {
      await apiClient.post('/api/v1/admin/knowledge-base/import', formData, {
        params: category ? { category } : undefined,
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      toast.success('Đã nhập tài liệu')
      setFile(null)
      onImported()
      onOpenChange(false)
    } catch (caught) {
      toast.error(caught instanceof Error ? caught.message : 'Không thể nhập tài liệu')
    } finally {
      setIsImporting(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Nhập tài liệu</DialogTitle>
          <DialogDescription>
            Hỗ trợ CSV, JSON, TXT hoặc Markdown có front matter.
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-4">
          <input
            type="file"
            accept=".csv,.json,.txt,.md"
            onChange={(event) => setFile(event.target.files?.[0] ?? null)}
          />
          <select
            className="h-10 w-full rounded-md border bg-white px-3 text-sm"
            value={category}
            onChange={(event) => setCategory(event.target.value as KnowledgeCategory | '')}
          >
            <option value="">Dùng danh mục trong file</option>
            {categoryOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
          <div className="flex justify-end gap-3">
            <Button variant="outline" onClick={() => onOpenChange(false)}>
              Hủy
            </Button>
            <Button onClick={() => void handleImport()} disabled={!file || isImporting}>
              {isImporting ? 'Đang nhập...' : 'Nhập'}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
