import { apiClient } from '@/lib/api/client'

export type FlaggedMessage = {
  message_id: string
  conversation_id: string
  bot_response: string
  user_query: string
  intent?: string | null
  intent_confidence?: number | null
  feedback_score?: number | null
  created_at: string
  retrieved_documents?: Array<Record<string, unknown>> | null
  reason: string
}

export type FlaggedMessageListResponse = {
  items: FlaggedMessage[]
  total: number
  skip: number
  limit: number
}

export type ReviewStatistics = {
  total_flagged: number
  pending: number
  approved: number
  rejected: number
  added_to_kb: number
  by_intent: Record<string, number>
  average_review_time_minutes?: number | null
  top_reviewers: Array<{ reviewer_id: string; reviewed_count: number }>
}

export type ReviewActionRequest = {
  corrected_content?: string
}

export type AddToKnowledgeBaseRequest = {
  category: string
  title: string
}

export async function getFlaggedMessages(params: {
  skip?: number
  limit?: number
  intent?: string
}): Promise<FlaggedMessageListResponse> {
  const response = await apiClient.get<FlaggedMessageListResponse>('/api/v1/admin/review/flagged', {
    params,
  })
  return response.data
}

export async function approveMessage(
  messageId: string,
  data: ReviewActionRequest
): Promise<boolean> {
  const response = await apiClient.post<boolean>(`/api/v1/admin/review/${messageId}/approve`, data)
  return response.data
}

export async function rejectMessage(messageId: string): Promise<boolean> {
  const response = await apiClient.post<boolean>(`/api/v1/admin/review/${messageId}/reject`)
  return response.data
}

export async function addToKnowledgeBase(
  messageId: string,
  data: AddToKnowledgeBaseRequest
): Promise<string> {
  const response = await apiClient.post<string>(`/api/v1/admin/review/${messageId}/add-to-kb`, data)
  return response.data
}

export async function getReviewStatistics(
  params: {
    date_from?: string
    date_to?: string
  } = {}
): Promise<ReviewStatistics> {
  const response = await apiClient.get<ReviewStatistics>('/api/v1/admin/review/statistics', {
    params,
  })
  return response.data
}
