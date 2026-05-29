'use client'

import { Keyboard, PlusCircle } from 'lucide-react'
import { useEffect, useState } from 'react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Textarea } from '@/components/ui/textarea'
import type { FlaggedMessage } from '@/lib/api/review'
import { AddToKbDialog } from './add-to-kb-dialog'

type AnnotationInterfaceProps = {
  message?: FlaggedMessage
  index: number
  total: number
  onApprove: (message: FlaggedMessage, correctedContent?: string) => void
  onReject: (message: FlaggedMessage) => void
  onAddToKb: (message: FlaggedMessage, payload: { category: string; title: string }) => void
  isSaving?: boolean
}

export function AnnotationInterface({
  message,
  index,
  total,
  onApprove,
  onReject,
  onAddToKb,
  isSaving,
}: AnnotationInterfaceProps) {
  const [correctedContent, setCorrectedContent] = useState('')
  const [kbDialogOpen, setKbDialogOpen] = useState(false)

  useEffect(() => {
    function handleKeyDown(event: KeyboardEvent) {
      if (
        !message ||
        event.target instanceof HTMLTextAreaElement ||
        event.target instanceof HTMLInputElement
      ) {
        return
      }
      if (event.key === 'a') onApprove(message)
      if (event.key === 'r') onReject(message)
      if (event.key === 'k') setKbDialogOpen(true)
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [message, onApprove, onReject])

  if (!message) {
    return (
      <Card>
        <CardContent className="py-20 text-center text-sm text-slate-500">
          Chọn một phản hồi để review.
        </CardContent>
      </Card>
    )
  }

  const hasCorrection = correctedContent.trim() && correctedContent.trim() !== message.bot_response

  return (
    <Card>
      <CardHeader className="space-y-3">
        <div className="flex items-center justify-between gap-3">
          <CardTitle className="text-lg">Review phản hồi</CardTitle>
          <Badge variant="outline">
            {index + 1} / {total}
          </Badge>
        </div>
        <div className="flex flex-wrap items-center gap-2 text-xs text-slate-500">
          <Keyboard className="h-3.5 w-3.5" />
          <span>a: phê duyệt</span>
          <span>r: từ chối</span>
          <span>k: thêm KB</span>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <section className="space-y-2">
          <p className="text-sm font-medium text-slate-700">Câu hỏi khách hàng</p>
          <div className="rounded-md bg-slate-100 p-3 text-sm text-slate-800">
            {message.user_query || 'Không có context'}
          </div>
        </section>
        <section className="space-y-2">
          <p className="text-sm font-medium text-slate-700">Phản hồi bot</p>
          <Textarea
            value={correctedContent}
            onChange={(event) => setCorrectedContent(event.target.value)}
            className="min-h-44"
          />
        </section>
        <section className="space-y-2">
          <p className="text-sm font-medium text-slate-700">Tài liệu đã truy xuất</p>
          <div className="rounded-md border bg-white p-3 text-xs text-slate-600">
            {message.retrieved_documents?.length
              ? `${message.retrieved_documents.length} tài liệu`
              : 'Không có tài liệu truy xuất'}
          </div>
        </section>
        <div className="flex flex-wrap gap-2">
          <Button disabled={isSaving} onClick={() => onApprove(message)}>
            Phê duyệt
          </Button>
          <Button
            disabled={isSaving || !hasCorrection}
            variant="outline"
            onClick={() => onApprove(message, correctedContent.trim())}
          >
            Phê duyệt với sửa đổi
          </Button>
          <Button disabled={isSaving} variant="outline" onClick={() => onReject(message)}>
            Từ chối
          </Button>
          <Button disabled={isSaving} variant="outline" onClick={() => setKbDialogOpen(true)}>
            <PlusCircle className="mr-2 h-4 w-4" />
            Thêm vào kiến thức
          </Button>
        </div>
      </CardContent>
      <AddToKbDialog
        message={message}
        open={kbDialogOpen}
        onOpenChange={setKbDialogOpen}
        isSaving={isSaving}
        onSave={(payload) => onAddToKb(message, payload)}
      />
    </Card>
  )
}
