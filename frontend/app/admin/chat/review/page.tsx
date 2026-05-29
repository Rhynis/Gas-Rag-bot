'use client'

import { useMemo, useState } from 'react'
import { AnnotationInterface } from '@/components/admin/review/annotation-interface'
import { FlaggedMessageList } from '@/components/admin/review/flagged-message-list'
import { ReviewStatistics } from '@/components/admin/review/review-statistics'
import {
  useAddToKnowledgeBase,
  useApproveMessage,
  useFlaggedMessages,
  useRejectMessage,
  useReviewStatistics,
} from '@/lib/hooks/use-review'
import type { FlaggedMessage } from '@/lib/api/review'

export default function AdminReviewPage() {
  const [selectedId, setSelectedId] = useState<string>()
  const flagged = useFlaggedMessages({ limit: 50 })
  const statistics = useReviewStatistics()
  const approve = useApproveMessage()
  const reject = useRejectMessage()
  const addToKb = useAddToKnowledgeBase()

  const messages = useMemo(() => flagged.data?.items ?? [], [flagged.data?.items])
  const selectedMessage = useMemo(
    () => messages.find((message) => message.message_id === selectedId) ?? messages[0],
    [messages, selectedId]
  )
  const selectedIndex = selectedMessage
    ? Math.max(
        0,
        messages.findIndex((message) => message.message_id === selectedMessage.message_id)
      )
    : 0

  function selectNext(current: FlaggedMessage) {
    const currentIndex = messages.findIndex((message) => message.message_id === current.message_id)
    const next = messages[currentIndex + 1] ?? messages[currentIndex - 1]
    setSelectedId(next?.message_id)
  }

  function handleApprove(message: FlaggedMessage, correctedContent?: string) {
    approve.mutate(
      {
        messageId: message.message_id,
        data: correctedContent ? { corrected_content: correctedContent } : {},
      },
      { onSuccess: () => selectNext(message) }
    )
  }

  function handleReject(message: FlaggedMessage) {
    reject.mutate(message.message_id, { onSuccess: () => selectNext(message) })
  }

  function handleAddToKb(message: FlaggedMessage, payload: { category: string; title: string }) {
    addToKb.mutate(
      { messageId: message.message_id, data: payload },
      { onSuccess: () => selectNext(message) }
    )
  }

  const isSaving = approve.isPending || reject.isPending || addToKb.isPending

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-slate-900">Review phản hồi</h1>
        <p className="text-sm text-slate-600">
          Xem phản hồi bị flag, phê duyệt, từ chối hoặc thêm vào Knowledge Base.
        </p>
      </div>
      <ReviewStatistics statistics={statistics.data} />
      <div className="grid gap-4 lg:grid-cols-[minmax(320px,0.9fr)_minmax(0,1.4fr)]">
        <FlaggedMessageList
          messages={messages}
          selectedId={selectedMessage?.message_id}
          onSelect={(message) => setSelectedId(message.message_id)}
          onApprove={(message) => handleApprove(message)}
          onReject={handleReject}
          onAddToKb={(message) => setSelectedId(message.message_id)}
        />
        <AnnotationInterface
          key={selectedMessage?.message_id ?? 'empty'}
          message={selectedMessage}
          index={selectedIndex}
          total={messages.length}
          isSaving={isSaving || flagged.isLoading}
          onApprove={handleApprove}
          onReject={handleReject}
          onAddToKb={handleAddToKb}
        />
      </div>
    </div>
  )
}
