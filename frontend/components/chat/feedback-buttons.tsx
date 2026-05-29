'use client'

import { ThumbsDown, ThumbsUp } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useSubmitFeedback } from '@/lib/hooks/use-conversation'
import type { Message } from '@/types/conversation'

type FeedbackButtonsProps = {
  conversationId: string
  message: Message
}

export function FeedbackButtons({ conversationId, message }: FeedbackButtonsProps) {
  const mutation = useSubmitFeedback()

  if (message.role !== 'assistant') return null

  return (
    <div className="mt-2 flex gap-1">
      <Button
        type="button"
        variant="ghost"
        size="icon"
        className="h-7 w-7"
        aria-label="Hài lòng"
        disabled={mutation.isPending}
        onClick={() =>
          mutation.mutate({ conversationId, messageId: message.id, data: { score: 1 } })
        }
      >
        <ThumbsUp className="h-3.5 w-3.5" />
      </Button>
      <Button
        type="button"
        variant="ghost"
        size="icon"
        className="h-7 w-7"
        aria-label="Chưa hài lòng"
        disabled={mutation.isPending}
        onClick={() =>
          mutation.mutate({ conversationId, messageId: message.id, data: { score: -1 } })
        }
      >
        <ThumbsDown className="h-3.5 w-3.5" />
      </Button>
    </div>
  )
}
