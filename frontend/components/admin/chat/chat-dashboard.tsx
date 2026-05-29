'use client'

import { AlertTriangle, MessageSquareText, RefreshCw } from 'lucide-react'
import Link from 'next/link'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { useStaffConversations } from '@/lib/hooks/use-conversation'
import { cn } from '@/lib/utils'

const statusLabels: Record<string, string> = {
  active: 'Đang hoạt động',
  escalated: 'Cần hỗ trợ',
  resolved: 'Đã xử lý',
  abandoned: 'Bỏ dở',
}

export function ChatDashboard() {
  const conversations = useStaffConversations({ status: 'escalated', limit: 50 })

  if (conversations.isLoading) {
    return (
      <div className="space-y-3">
        <Skeleton className="h-24" />
        <Skeleton className="h-24" />
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">Chat hỗ trợ</h1>
          <p className="text-sm text-slate-600">Cuộc trò chuyện cần nhân viên xử lý</p>
        </div>
        <Button type="button" variant="outline" onClick={() => conversations.refetch()}>
          <RefreshCw className="mr-2 h-4 w-4" />
          Làm mới
        </Button>
      </div>

      <div className="grid gap-3 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-slate-600">Đang chờ</CardTitle>
          </CardHeader>
          <CardContent className="text-3xl font-semibold">
            {conversations.data?.total ?? 0}
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-slate-600">Khẩn cấp</CardTitle>
          </CardHeader>
          <CardContent className="text-3xl font-semibold text-red-700">
            {conversations.data?.items.filter((item) =>
              item.messages.some((message) => message.is_emergency)
            ).length ?? 0}
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-slate-600">Bị flag</CardTitle>
          </CardHeader>
          <CardContent className="text-3xl font-semibold text-amber-700">
            {conversations.data?.items.filter((item) =>
              item.messages.some((message) => message.flagged_for_review)
            ).length ?? 0}
          </CardContent>
        </Card>
      </div>

      <div className="space-y-2">
        {conversations.data?.items.length ? (
          conversations.data.items.map((conversation) => {
            const lastMessage = conversation.messages[conversation.messages.length - 1]
            const hasEmergency = conversation.messages.some((message) => message.is_emergency)
            return (
              <Link
                key={conversation.id}
                href={`/admin/chat/${conversation.id}`}
                className="block rounded-lg border bg-white p-4 transition hover:border-slate-400"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0 space-y-1">
                    <div className="flex items-center gap-2">
                      <MessageSquareText className="h-4 w-4 text-slate-500" />
                      <p className="truncate text-sm font-semibold text-slate-900">
                        Session {conversation.session_id}
                      </p>
                    </div>
                    <p className="truncate text-sm text-slate-600">
                      {lastMessage?.content ?? 'Chưa có tin nhắn'}
                    </p>
                  </div>
                  <div className="flex shrink-0 items-center gap-2">
                    {hasEmergency ? <AlertTriangle className="h-4 w-4 text-red-700" /> : null}
                    <Badge
                      variant="outline"
                      className={cn(
                        conversation.status === 'escalated' && 'border-sky-300 text-sky-800',
                        conversation.status === 'resolved' && 'border-emerald-300 text-emerald-800'
                      )}
                    >
                      {statusLabels[conversation.status] ?? conversation.status}
                    </Badge>
                  </div>
                </div>
              </Link>
            )
          })
        ) : (
          <div className="rounded-lg border bg-white p-10 text-center text-sm text-slate-500">
            Không có cuộc trò chuyện cần xử lý.
          </div>
        )}
      </div>
    </div>
  )
}
