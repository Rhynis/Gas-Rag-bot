'use client'

import { MessageCircle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useChatStore } from '@/lib/stores/chat-store'
import { ChatWindow } from './chat-window'

export function ChatWidget() {
  const isOpen = useChatStore((state) => state.isOpen)
  const toggle = useChatStore((state) => state.toggle)

  return (
    <>
      {isOpen ? <ChatWindow /> : null}
      <Button
        type="button"
        size="icon"
        className="fixed bottom-6 right-4 z-50 h-14 w-14 rounded-full shadow-lg md:right-6"
        aria-label="Mở chat hỗ trợ"
        onClick={toggle}
      >
        <MessageCircle className="h-6 w-6" />
      </Button>
    </>
  )
}
