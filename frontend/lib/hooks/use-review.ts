'use client'

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import * as reviewApi from '@/lib/api/review'
import type { AddToKnowledgeBaseRequest, ReviewActionRequest } from '@/lib/api/review'

export const reviewKeys = {
  all: ['review'] as const,
  flagged: (params: Record<string, unknown>) => [...reviewKeys.all, 'flagged', params] as const,
  statistics: () => [...reviewKeys.all, 'statistics'] as const,
}

export function useFlaggedMessages(params: { skip?: number; limit?: number; intent?: string }) {
  return useQuery({
    queryKey: reviewKeys.flagged(params),
    queryFn: () => reviewApi.getFlaggedMessages(params),
  })
}

export function useReviewStatistics() {
  return useQuery({
    queryKey: reviewKeys.statistics(),
    queryFn: () => reviewApi.getReviewStatistics(),
  })
}

export function useApproveMessage() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ messageId, data }: { messageId: string; data: ReviewActionRequest }) =>
      reviewApi.approveMessage(messageId, data),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: reviewKeys.all })
      toast.success('Đã phê duyệt phản hồi')
    },
  })
}

export function useRejectMessage() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (messageId: string) => reviewApi.rejectMessage(messageId),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: reviewKeys.all })
      toast.success('Đã từ chối phản hồi')
    },
  })
}

export function useAddToKnowledgeBase() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ messageId, data }: { messageId: string; data: AddToKnowledgeBaseRequest }) =>
      reviewApi.addToKnowledgeBase(messageId, data),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: reviewKeys.all })
      toast.success('Đã thêm vào Knowledge Base')
    },
  })
}
