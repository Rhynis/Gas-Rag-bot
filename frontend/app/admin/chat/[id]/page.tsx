import { ChatDetailStaff } from '@/components/admin/chat/chat-detail-staff'

type AdminChatDetailPageProps = {
  params: Promise<{ id: string }>
}

export default async function AdminChatDetailPage({ params }: AdminChatDetailPageProps) {
  const { id } = await params
  return <ChatDetailStaff conversationId={id} />
}
