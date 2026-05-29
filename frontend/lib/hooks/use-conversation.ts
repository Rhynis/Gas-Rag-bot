'use client'

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import * as conversationsApi from '@/lib/api/conversations'
import { useChatStore } from '@/lib/stores/chat-store'
import type {
  FeedbackRequest,
  ResolveRequest,
  SendMessageRequest,
  StaffMessageRequest,
  StartConversationRequest,
  TransferRequest,
} from '@/types/conversation'

export const conversationKeys = {
  all: ['conversations'] as const,
  active: (sessionId: string) => [...conversationKeys.all, 'active', sessionId] as const,
  detail: (conversationId: string) => [...conversationKeys.all, 'detail', conversationId] as const,
  messages: (conversationId: string) =>
    [...conversationKeys.all, 'messages', conversationId] as const,
  staffList: (params: Record<string, unknown>) =>
    [...conversationKeys.all, 'staff', params] as const,
}

export function useStartConversation() {
  const queryClient = useQueryClient()
  const setConversationId = useChatStore((state) => state.setConversationId)

  return useMutation({
    mutationFn: (data: StartConversationRequest) => conversationsApi.startConversation(data),
    onSuccess: async (conversation) => {
      setConversationId(conversation.id)
      queryClient.setQueryData(conversationKeys.detail(conversation.id), conversation)
      await queryClient.invalidateQueries({ queryKey: conversationKeys.all })
    },
  })
}

export function useActiveConversation(sessionId: string, enabled = true) {
  return useQuery({
    queryKey: conversationKeys.active(sessionId),
    queryFn: () => conversationsApi.getActiveConversation(sessionId),
    enabled,
  })
}

export function useConversation(conversationId?: string) {
  return useQuery({
    queryKey: conversationKeys.detail(conversationId ?? ''),
    queryFn: () => conversationsApi.getConversation(conversationId ?? ''),
    enabled: Boolean(conversationId),
  })
}

export function useMessages(conversationId?: string, enabled = true) {
  const isOpen = useChatStore((state) => state.isOpen)

  return useQuery({
    queryKey: conversationKeys.messages(conversationId ?? ''),
    queryFn: () => conversationsApi.listMessages(conversationId ?? ''),
    enabled: Boolean(conversationId) && enabled,
    refetchInterval: isOpen && conversationId ? 3000 : false,
  })
}

export function useSendMessage() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ conversationId, data }: { conversationId: string; data: SendMessageRequest }) =>
      conversationsApi.sendMessage(conversationId, data),
    onSuccess: async (response) => {
      queryClient.setQueryData(
        conversationKeys.detail(response.conversation.id),
        response.conversation
      )
      await queryClient.invalidateQueries({
        queryKey: conversationKeys.messages(response.conversation.id),
      })
      if (response.assistant_message?.is_emergency) {
        toast.error('Khẩn cấp an toàn gas: gọi 1900-1234 ngay')
      }
    },
  })
}

export function useSubmitFeedback() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({
      conversationId,
      messageId,
      data,
    }: {
      conversationId: string
      messageId: string
      data: FeedbackRequest
    }) => conversationsApi.submitFeedback(conversationId, messageId, data),
    onSuccess: async (_message, variables) => {
      await queryClient.invalidateQueries({
        queryKey: conversationKeys.messages(variables.conversationId),
      })
    },
  })
}

export function useStaffConversations(params: { status?: string; skip?: number; limit?: number }) {
  return useQuery({
    queryKey: conversationKeys.staffList(params),
    queryFn: () => conversationsApi.listStaffConversations(params),
    refetchInterval: 3000,
  })
}

export function useSendStaffMessage() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ conversationId, data }: { conversationId: string; data: StaffMessageRequest }) =>
      conversationsApi.sendStaffMessage(conversationId, data),
    onSuccess: async (_message, variables) => {
      await queryClient.invalidateQueries({
        queryKey: conversationKeys.messages(variables.conversationId),
      })
      await queryClient.invalidateQueries({ queryKey: conversationKeys.all })
    },
  })
}

export function useTransferConversation() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ conversationId, data }: { conversationId: string; data: TransferRequest }) =>
      conversationsApi.transferConversation(conversationId, data),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: conversationKeys.all })
    },
  })
}

export function useResolveConversation() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ conversationId, data }: { conversationId: string; data?: ResolveRequest }) =>
      conversationsApi.resolveConversation(conversationId, data),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: conversationKeys.all })
      toast.success('Đã kết thúc cuộc trò chuyện')
    },
  })
}
