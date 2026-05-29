'use client'

import { v4 as uuidv4 } from 'uuid'
import { create } from 'zustand'
import { createJSONStorage, persist } from 'zustand/middleware'

type ChatState = {
  isOpen: boolean
  sessionId: string
  conversationId?: string
  open: () => void
  close: () => void
  toggle: () => void
  setConversationId: (conversationId?: string) => void
  resetSession: () => void
}

export const useChatStore = create<ChatState>()(
  persist(
    (set) => ({
      isOpen: false,
      sessionId: uuidv4(),
      conversationId: undefined,
      open: () => set({ isOpen: true }),
      close: () => set({ isOpen: false }),
      toggle: () => set((state) => ({ isOpen: !state.isOpen })),
      setConversationId: (conversationId) => set({ conversationId }),
      resetSession: () => set({ sessionId: uuidv4(), conversationId: undefined }),
    }),
    {
      name: 'gasbot-chat',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        sessionId: state.sessionId,
        conversationId: state.conversationId,
      }),
    }
  )
)
