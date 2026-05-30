'use client'

import { AlertCircle, MessageSquareText } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'
import { cn } from '@/lib/utils'
import type { FlaggedMessage } from '@/lib/api/review'

type FlaggedMessageListProps = {
  messages: FlaggedMessage[]
  selectedId?: string
  onSelect: (message: FlaggedMessage) => void
  onApprove: (message: FlaggedMessage) => void
  onReject: (message: FlaggedMessage) => void
  onAddToKb: (message: FlaggedMessage) => void
}

export function FlaggedMessageList({
  messages,
  selectedId,
  onSelect,
  onApprove,
  onReject,
  onAddToKb,
}: FlaggedMessageListProps) {
  return (
    <ScrollArea className="h-[640px] rounded-lg border bg-white">
      <div className="space-y-2 p-3">
        {messages.length === 0 ? (
          <div className="py-16 text-center text-sm text-slate-500">
            Không có phản hồi cần review.
          </div>
        ) : (
          messages.map((message) => (
            <article
              key={message.message_id}
              className={cn(
                'rounded-md border p-3 transition',
                selectedId === message.message_id
                  ? 'border-slate-900 bg-slate-50'
                  : 'border-slate-200 hover:border-slate-400'
              )}
            >
              <button type="button" className="w-full text-left" onClick={() => onSelect(message)}>
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0 space-y-1">
                    <div className="flex items-center gap-2">
                      <MessageSquareText className="h-4 w-4 text-slate-500" />
                      <p className="truncate text-sm font-semibold text-slate-900">
                        {message.user_query || 'Không có context'}
                      </p>
                    </div>
                    <p className="line-clamp-2 text-sm text-slate-600">{message.bot_response}</p>
                  </div>
                  <AlertCircle className="h-4 w-4 shrink-0 text-red-700" />
                </div>
                <div className="mt-3 flex flex-wrap gap-2">
                  <Badge variant="outline">{message.intent ?? 'unknown'}</Badge>
                  <Badge variant="outline">{message.reason}</Badge>
                </div>
              </button>
              <div className="mt-3 flex gap-2">
                <Button size="sm" variant="outline" onClick={() => onApprove(message)}>
                  Phê duyệt
                </Button>
                <Button size="sm" variant="outline" onClick={() => onReject(message)}>
                  Từ chối
                </Button>
                <Button size="sm" onClick={() => onAddToKb(message)}>
                  Thêm KB
                </Button>
              </div>
            </article>
          ))
        )}
      </div>
    </ScrollArea>
  )
}
