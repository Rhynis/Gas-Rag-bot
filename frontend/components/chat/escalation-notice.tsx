import { Headphones } from 'lucide-react'

type EscalationNoticeProps = {
  reason?: string | null
}

export function EscalationNotice({ reason }: EscalationNoticeProps) {
  return (
    <div className="rounded-md border border-sky-200 bg-sky-50 p-3 text-sm text-sky-900">
      <div className="flex items-start gap-2">
        <Headphones className="mt-0.5 h-4 w-4 shrink-0" />
        <div>
          <p className="font-semibold">Nhân viên đang hỗ trợ</p>
          <p>{reason ?? 'Cuộc trò chuyện đã được chuyển cho đội hỗ trợ.'}</p>
        </div>
      </div>
    </div>
  )
}
