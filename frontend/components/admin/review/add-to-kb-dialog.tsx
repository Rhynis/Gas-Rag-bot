'use client'

import { FormEvent, useState } from 'react'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import type { FlaggedMessage } from '@/lib/api/review'

const categories = [
  { value: 'faq', label: 'FAQ' },
  { value: 'safety', label: 'An toàn' },
  { value: 'product_info', label: 'Sản phẩm' },
  { value: 'delivery', label: 'Giao hàng' },
  { value: 'pricing', label: 'Giá' },
  { value: 'technical', label: 'Kỹ thuật' },
  { value: 'company', label: 'Công ty' },
]

type AddToKbDialogProps = {
  message?: FlaggedMessage
  open: boolean
  onOpenChange: (open: boolean) => void
  onSave: (payload: { category: string; title: string }) => void
  isSaving?: boolean
}

export function AddToKbDialog({
  message,
  open,
  onOpenChange,
  onSave,
  isSaving,
}: AddToKbDialogProps) {
  const [category, setCategory] = useState('faq')
  const [title, setTitle] = useState('')

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!title.trim()) return
    onSave({ category, title: title.trim() })
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Thêm vào Knowledge Base</DialogTitle>
          <DialogDescription>
            Nội dung sẽ dùng bản đã sửa nếu phản hồi đã được phê duyệt với chỉnh sửa.
          </DialogDescription>
        </DialogHeader>
        <form className="space-y-4" onSubmit={handleSubmit}>
          <div className="space-y-2">
            <Label>Danh mục</Label>
            <Select value={category} onValueChange={setCategory}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {categories.map((item) => (
                  <SelectItem key={item.value} value={item.value}>
                    {item.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label htmlFor="kb-title">Tiêu đề</Label>
            <Input
              id="kb-title"
              value={title}
              onChange={(event) => setTitle(event.target.value)}
              placeholder="Ví dụ: Hướng dẫn xử lý mùi gas"
            />
          </div>
          <div className="space-y-2">
            <Label>Nội dung xem trước</Label>
            <Textarea value={message?.bot_response ?? ''} readOnly className="min-h-32" />
          </div>
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Hủy
            </Button>
            <Button type="submit" disabled={isSaving || !title.trim()}>
              Lưu
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
