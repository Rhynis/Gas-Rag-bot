import { Bot, UserRound } from 'lucide-react'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { cn } from '@/lib/utils'
import type { Message } from '@/types/conversation'
import { FeedbackButtons } from './feedback-buttons'

type MessageBubbleProps = {
  conversationId: string
  message: Message
}

export function MessageBubble({ conversationId, message }: MessageBubbleProps) {
  const isUser = message.role === 'user'
  const isStaff = message.role === 'staff'

  return (
    <div className={cn('flex gap-2', isUser && 'flex-row-reverse')}>
      <Avatar className="h-8 w-8">
        <AvatarFallback
          className={cn(isUser ? 'bg-slate-900 text-white' : 'bg-sky-100 text-sky-800')}
        >
          {isUser ? <UserRound className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
        </AvatarFallback>
      </Avatar>
      <div className={cn('max-w-[78%]', isUser && 'items-end text-right')}>
        <div
          className={cn(
            'rounded-lg px-3 py-2 text-sm leading-6',
            isUser && 'bg-slate-900 text-white',
            !isUser && !isStaff && 'bg-white text-slate-800 shadow-sm ring-1 ring-slate-200',
            isStaff && 'bg-sky-700 text-white'
          )}
        >
          {message.content}
        </div>
        <FeedbackButtons conversationId={conversationId} message={message} />
      </div>
    </div>
  )
}
